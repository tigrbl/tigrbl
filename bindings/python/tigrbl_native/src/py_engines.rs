use crate::callback_registry::descriptor;

pub fn register_python_engine(name: &str) -> String {
    descriptor("python-engine", name)
}
