use std::collections::BTreeMap;

use tigrbl_rs_spec::values::Value;

pub type Body = Value;
pub type Path = BTreeMap<String, Value>;
pub type Query = BTreeMap<String, Value>;
pub type Param = BTreeMap<String, Value>;
pub type Header = BTreeMap<String, String>;
