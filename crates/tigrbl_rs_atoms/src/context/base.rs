use std::collections::BTreeMap;

use tigrbl_rs_spec::{request::RequestEnvelope, response::ResponseEnvelope, values::Value};

#[derive(Debug, Clone, Default, PartialEq)]
pub struct AtomContext {
    pub request: RequestEnvelope,
    pub response: Option<ResponseEnvelope>,
    pub scratch: BTreeMap<String, Value>,
}
