use std::collections::BTreeMap;

#[derive(Debug, Clone, Default, PartialEq)]
pub enum Value {
    #[default]
    Null,
    Bool(bool),
    Integer(i64),
    Float(f64),
    String(String),
    Bytes(Vec<u8>),
    Array(Vec<Value>),
    Object(BTreeMap<String, Value>),
}
