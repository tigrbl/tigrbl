use tigrbl_rs_ports::{engines::EnginePort, errors::PortResult, sessions::SessionPort};

use crate::session::SqliteSession;

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct SqliteEngine;

impl EnginePort for SqliteEngine {
    fn kind(&self) -> &str {
        "sqlite"
    }

    fn open(&self) -> PortResult<Box<dyn SessionPort>> {
        Ok(Box::new(SqliteSession::default()))
    }
}
