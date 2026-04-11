use tigrbl_rs_ports::{CallbackKind, CallbackRef, PortError};

#[test]
fn port_error_formats_not_implemented_variant() {
    let err = PortError::not_implemented("engine.open");
    assert_eq!(format!("{err}"), "not implemented: engine.open");
}

#[test]
fn callback_ref_preserves_kind_and_name() {
    let callback = CallbackRef {
        kind: CallbackKind::Python,
        name: "demo.handler".to_string(),
    };

    assert_eq!(callback.kind, CallbackKind::Python);
    assert_eq!(callback.name, "demo.handler");
}
