use crate::callback_registry::descriptor;

pub fn register_python_handler(name: &str) -> String {
    crate::callback_registry::record_event(
        "register_python_handler",
        serde_json::json!({"name": name}),
    );
    descriptor("python-handler", name)
}
