use tigrbl_rs_ports::{engines::EnginePort, errors::PortResult, sessions::SessionPort};

use crate::session::PostgresSession;

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct PostgresEngine;

impl EnginePort for PostgresEngine {
    fn kind(&self) -> &str {
        "postgres"
    }

    fn open(&self) -> PortResult<Box<dyn SessionPort>> {
        Ok(Box::new(PostgresSession::default()))
    }
}
