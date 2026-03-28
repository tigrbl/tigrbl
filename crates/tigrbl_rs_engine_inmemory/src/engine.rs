use tigrbl_rs_ports::{engines::EnginePort, errors::PortResult, sessions::SessionPort};

use crate::session::InmemorySession;

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct InmemoryEngine;

impl EnginePort for InmemoryEngine {
    fn kind(&self) -> &str {
        "inmemory"
    }

    fn open(&self) -> PortResult<Box<dyn SessionPort>> {
        Ok(Box::new(InmemorySession::default()))
    }
}
