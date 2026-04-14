use crate::callback_registry::descriptor;

pub fn register_python_engine(name: &str) -> String {
    crate::callback_registry::record_event(
        "register_python_engine",
        serde_json::json!({"name": name}),
    );
    descriptor("python-engine", name)
}
