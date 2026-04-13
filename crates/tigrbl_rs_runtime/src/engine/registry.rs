use std::collections::BTreeMap;

use tigrbl_rs_engine_inmemory::engine::InmemoryEngine;
use tigrbl_rs_ports::engines::EnginePort;

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

    pub fn register(&mut self, engine: Box<dyn EnginePort>) {
        self.engines.insert(engine.kind().to_string(), engine);
    }

    pub fn get(&self, kind: &str) -> Option<&dyn EnginePort> {
        self.engines.get(kind).map(Box::as_ref)
    }
}
