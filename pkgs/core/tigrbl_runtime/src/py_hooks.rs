use crate::callback_registry::descriptor;

pub fn register_python_hook(name: &str) -> String {
    crate::callback_registry::record_event(
        "register_python_hook",
        serde_json::json!({"name": name}),
    );
    descriptor("python-hook", name)
}
