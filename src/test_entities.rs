use ocs_plugin_api::host::codec::entities::{Point, Line, Circle, Text};
use ocs_plugin_api::host::codec::{EntityType, Handle};

#[test]
fn test_entities() {
    let mut pt = Point::from_coords(1.0, 2.0, 3.0);
    pt.common.layer = "0".to_string();
    let _ = EntityType::Point(pt);
}
