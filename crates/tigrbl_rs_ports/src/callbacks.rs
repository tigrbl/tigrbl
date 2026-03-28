use crate::errors::PortResult;
use tigrbl_rs_spec::values::Value;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum CallbackKind {
    Rust,
    Python,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CallbackRef {
    pub kind: CallbackKind,
    pub name: String,
}

pub trait CallbackPort: Send + Sync {
    fn invoke(&self, callback: &CallbackRef, payload: Value) -> PortResult<Value>;
}
