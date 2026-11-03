# OpenCAD AutoLISP & IDE Runner (`opencad-autolisp-and-ide`) — Agent Instructions

## CRITICAL RULE: Python Support is SHELVED / FROZEN

1. **Do NOT touch Python files**:
   - All Python modules (`py_module.rs`, `py_runtime.rs`, `py_debug.rs`, `py_sandbox.rs`) and the legacy `autolisp.py` prototype have been moved to `archive/python_shelved/` and disabled behind the off-by-default Cargo feature `python`.
   - **NEVER** modify, update, or add features to any file in `archive/python_shelved/`.
   - **NEVER** attempt to mirror AutoLISP additions into Python or `autolisp.py`.

2. **Where All AutoLISP Development Lives**:
   - **Core AutoLISP Evaluator & Built-ins**: `../opencad-autolisp-engine/crates/lisp-core`
   - **AutoLISP CAD / DOSLib / VL / VLAX / GUI Functions & `CadBridge` Trait**: `../opencad-autolisp-engine/crates/lisp-cad`
   - **OpenCAD Studio Host IPC Bridge (`OpenCadRustBridge`)**: `src/rust_lisp.rs`
   - **OCAIDE Standalone Editor/REPL**: `src/ide/`
