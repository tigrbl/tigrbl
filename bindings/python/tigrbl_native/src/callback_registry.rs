use std::sync::{Mutex, OnceLock};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CallbackRegistration {
    pub kind: String,
    pub name: String,
}

fn registrations() -> &'static Mutex<Vec<CallbackRegistration>> {
    static REGISTRY: OnceLock<Mutex<Vec<CallbackRegistration>>> = OnceLock::new();
    REGISTRY.get_or_init(|| Mutex::new(Vec::new()))
}

fn boundary_events() -> &'static Mutex<Vec<serde_json::Value>> {
    static EVENTS: OnceLock<Mutex<Vec<serde_json::Value>>> = OnceLock::new();
    EVENTS.get_or_init(|| Mutex::new(Vec::new()))
}

pub fn descriptor(kind: &str, name: &str) -> String {
    let registration = CallbackRegistration {
        kind: kind.to_string(),
        name: name.to_string(),
    };
    registrations()
        .lock()
        .expect("callback registry lock poisoned")
        .push(registration.clone());
    record_event(
        "register_callback",
        serde_json::json!({"kind": registration.kind, "name": registration.name}),
    );
    format!("{kind}:{name}")
}

pub fn record_event(event: &str, payload: serde_json::Value) {
    boundary_events()
        .lock()
        .expect("boundary events lock poisoned")
        .push(serde_json::json!({"event": event, "payload": payload}));
}

pub fn ffi_boundary_events() -> Vec<serde_json::Value> {
    boundary_events()
        .lock()
        .expect("boundary events lock poisoned")
        .clone()
}

pub fn clear_ffi_boundary_events() {
    boundary_events()
        .lock()
        .expect("boundary events lock poisoned")
        .clear();
}
