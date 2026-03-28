use std::collections::BTreeMap;

use crate::{BindingSpec, EngineSpec, TableSpec};

#[derive(Debug, Clone, PartialEq)]
pub struct AppSpec {
    pub name: String,
    pub title: String,
    pub version: String,
    pub bindings: Vec<BindingSpec>,
    pub tables: Vec<TableSpec>,
    pub engines: Vec<EngineSpec>,
    pub jsonrpc_prefix: String,
    pub system_prefix: String,
    pub metadata: BTreeMap<String, String>,
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
            jsonrpc_prefix: String::from("/rpc"),
            system_prefix: String::from("/system"),
            metadata: BTreeMap::new(),
        }
    }
}
