use std::sync::{Arc, Mutex};

use tigrbl_rs_ports::{engines::EnginePort, errors::PortResult, sessions::SessionPort};

use crate::{session::InmemorySession, tx::Store};

#[derive(Debug, Clone, Default)]
pub struct InmemoryEngine {
    shared: Arc<Mutex<Store>>,
}

impl InmemoryEngine {
    pub fn new() -> Self {
        Self::default()
    }
}

impl EnginePort for InmemoryEngine {
    fn kind(&self) -> &str {
        "inmemory"
    }

    fn open(&self) -> PortResult<Box<dyn SessionPort>> {
        Ok(Box::new(InmemorySession::new(self.shared.clone())))
    }
}
