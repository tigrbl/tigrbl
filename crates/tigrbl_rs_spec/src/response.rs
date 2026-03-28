use std::collections::BTreeMap;

use crate::values::Value;

#[derive(Debug, Clone, Default, PartialEq)]
pub struct ResponseEnvelope {
    pub status: u16,
    pub headers: BTreeMap<String, String>,
    pub body: Value,
}
