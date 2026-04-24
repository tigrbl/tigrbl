use std::collections::BTreeMap;

use tigrbl_rs_engine_inmemory::engine::InmemoryEngine;
use tigrbl_rs_engine_sqlite::engine::SqliteEngine;
use tigrbl_rs_kernel::KernelPlan;
use tigrbl_rs_ports::engines::EnginePort;
use tigrbl_rs_spec::Value;

#[derive(Default)]
pub struct EngineRegistry {
    engines: BTreeMap<String, Box<dyn EnginePort>>,
}

impl EngineRegistry {
    pub fn new() -> Self {
        let mut registry = Self::default();
        registry.register(Box::new(InmemoryEngine::new()));
        registry
    }

    pub fn from_plan(plan: &KernelPlan) -> Self {
        let mut registry = Self::new();
        if plan.engine_kind == "sqlite" {
            registry.register(Box::new(SqliteEngine::new(sqlite_path(
                &plan.engine_options,
            ))));
        }
        registry
    }

    pub fn register(&mut self, engine: Box<dyn EnginePort>) {
        self.engines.insert(engine.kind().to_string(), engine);
    }

    pub fn get(&self, kind: &str) -> Option<&dyn EnginePort> {
        self.engines.get(kind).map(Box::as_ref)
    }
}

fn sqlite_path(options: &Value) -> Option<String> {
    let object = match options {
        Value::Object(object) => object,
        _ => return None,
    };
    match object.get("path") {
        Some(Value::String(path)) if !path.trim().is_empty() => Some(path.clone()),
        _ => None,
    }
}
