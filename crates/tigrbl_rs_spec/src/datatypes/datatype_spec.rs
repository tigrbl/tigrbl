use std::collections::BTreeMap;

use crate::values::Value;

#[derive(Debug, Clone, Default, PartialEq)]
pub struct DataTypeSpec {
    pub logical_name: String,
    pub nullable: bool,
    pub options: BTreeMap<String, Value>,
}

impl DataTypeSpec {
    pub fn new(logical_name: impl Into<String>) -> Self {
        Self {
            logical_name: logical_name.into(),
            nullable: false,
            options: BTreeMap::new(),
        }
    }
}
