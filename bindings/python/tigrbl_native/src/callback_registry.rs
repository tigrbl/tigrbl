#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CallbackRegistration {
    pub kind: String,
    pub name: String,
}

pub fn descriptor(kind: &str, name: &str) -> String {
    format!("{kind}:{name}")
}
