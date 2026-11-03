use std::io::{BufRead, BufReader, Write};
use std::net::TcpStream;
use std::sync::mpsc::{channel, Receiver, Sender};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

use crate::ide::protocol::{port_file_path, IdeToPlugin, PluginToIde};

#[derive(Clone)]
pub struct IdeClient {
    tx: Sender<IdeToPlugin>,
    connected: Arc<Mutex<bool>>,
}

impl IdeClient {
    pub fn new() -> (Self, Receiver<PluginToIde>) {
        let (req_tx, req_rx) = channel::<IdeToPlugin>();
        let (resp_tx, resp_rx) = channel::<PluginToIde>();
        let connected = Arc::new(Mutex::new(false));
        let connected_clone = Arc::clone(&connected);

        thread::spawn(move || {
            loop {
                // Try reading port file
                let port_opt = port_file_path().exists().then(|| {
                    std::fs::read_to_string(port_file_path()).ok().and_then(|s| s.trim().parse::<u16>().ok())
                }).flatten();

                if let Some(port) = port_opt {
                    if let Ok(stream) = TcpStream::connect(("127.0.0.1", port)) {
                        let _ = stream.set_nodelay(true);
                        *connected_clone.lock().unwrap() = true;
                        let _ = resp_tx.send(PluginToIde::ConsoleOutput {
                            text: format!("[IDE] Connected to OpenCAD Studio plugin on port {port}.\n"),
                            is_error: false,
                        });

                        let read_stream = match stream.try_clone() {
                            Ok(s) => s,
                            Err(_) => {
                                thread::sleep(Duration::from_millis(1000));
                                continue;
                            }
                        };
                        let write_stream = Arc::new(Mutex::new(stream));

                        // Spawn listener thread for incoming responses
                        let resp_tx_clone = resp_tx.clone();
                        let connected_reader = Arc::clone(&connected_clone);
                        let reader_handle = thread::spawn(move || {
                            let reader = BufReader::new(read_stream);
                            for line in reader.lines() {
                                let Ok(line) = line else { break };
                                if let Ok(msg) = serde_json::from_str::<PluginToIde>(&line) {
                                    if resp_tx_clone.send(msg).is_err() {
                                        break;
                                    }
                                }
                            }
                            *connected_reader.lock().unwrap() = false;
                            let _ = resp_tx_clone.send(PluginToIde::HostClosing);
                        });

                        // Writer loop handling outgoing requests
                        while let Ok(req) = req_rx.recv() {
                            let Ok(json) = serde_json::to_string(&req) else { continue };
                            let line = format!("{json}\n");
                            let mut s = write_stream.lock().unwrap();
                            if s.write_all(line.as_bytes()).is_err() || s.flush().is_err() {
                                break;
                            }
                        }

                        *connected_clone.lock().unwrap() = false;
                        let _ = reader_handle.join();
                    }
                }

                *connected_clone.lock().unwrap() = false;
                thread::sleep(Duration::from_millis(1500));
            }
        });

        (Self { tx: req_tx, connected }, resp_rx)
    }

    pub fn is_connected(&self) -> bool {
        *self.connected.lock().unwrap()
    }

    pub fn send(&self, req: IdeToPlugin) {
        let _ = self.tx.send(req);
    }
}
