use std::collections::BTreeMap;

use crate::values::Value;

#[derive(Debug, Clone, Default, PartialEq)]
pub struct RequestEnvelope {
    pub operation: String,
    pub path_params: BTreeMap<String, Value>,
    pub query_params: BTreeMap<String, Value>,
    pub headers: BTreeMap<String, String>,
    pub body: Value,
}
