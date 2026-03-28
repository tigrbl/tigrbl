use std::collections::BTreeMap;

use crate::values::Value;

#[derive(Debug, Clone, Default, PartialEq)]
pub struct EngineSpec {
    pub name: String,
    pub kind: String,
    pub options: BTreeMap<String, Value>,
}
