use crate::callback_registry::descriptor;

pub fn register_python_atom(name: &str) -> String {
    descriptor("python-atom", name)
}
