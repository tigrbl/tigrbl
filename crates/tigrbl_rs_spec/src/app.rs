use std::collections::BTreeMap;

use crate::{values::Value, BindingSpec, CallbackSpec, EngineSpec, TableSpec};

#[derive(Debug, Clone, PartialEq)]
pub struct AppSpec {
    pub name: String,
    pub title: String,
    pub version: String,
    pub bindings: Vec<BindingSpec>,
    pub tables: Vec<TableSpec>,
    pub engines: Vec<EngineSpec>,
    pub callbacks: Vec<CallbackSpec>,
    pub jsonrpc_prefix: String,
    pub system_prefix: String,
    pub metadata: BTreeMap<String, String>,
    pub runtime: BTreeMap<String, Value>,
    pub dependencies: Value,
    pub security: Value,
}

impl Default for AppSpec {
    fn default() -> Self {
        Self {
            name: String::new(),
            title: String::new(),
            version: String::from("0.1.0"),
            bindings: Vec::new(),
            tables: Vec::new(),
            engines: Vec::new(),
            callbacks: Vec::new(),
            jsonrpc_prefix: String::from("/rpc"),
            system_prefix: String::from("/system"),
            metadata: BTreeMap::new(),
            runtime: BTreeMap::new(),
            dependencies: Value::Null,
            security: Value::Null,
        }
    }
}
