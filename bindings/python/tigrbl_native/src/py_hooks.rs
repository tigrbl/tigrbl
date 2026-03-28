use crate::callback_registry::descriptor;

pub fn register_python_hook(name: &str) -> String {
    descriptor("python-hook", name)
}
