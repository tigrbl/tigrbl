use crate::callback_registry::descriptor;

pub fn register_python_handler(name: &str) -> String {
    descriptor("python-handler", name)
}
