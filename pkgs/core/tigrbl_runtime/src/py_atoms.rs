use crate::callback_registry::descriptor;

pub fn register_python_atom(name: &str) -> String {
    crate::callback_registry::record_event(
        "register_python_atom",
        serde_json::json!({"name": name}),
    );
    descriptor("python-atom", name)
}
