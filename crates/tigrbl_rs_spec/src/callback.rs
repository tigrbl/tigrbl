use crate::values::Value;

#[derive(Debug, Clone, Default, PartialEq)]
pub struct CallbackSpec {
    pub name: String,
    pub kind: String,
    pub language: String,
    pub target: Option<String>,
    pub metadata: Value,
}
