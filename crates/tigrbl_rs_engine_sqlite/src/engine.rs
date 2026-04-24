use tigrbl_rs_ports::{engines::EnginePort, errors::PortResult, sessions::SessionPort};

use crate::session::SqliteSession;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SqliteEngine {
    path: String,
    tables: Vec<String>,
}

impl Default for SqliteEngine {
    fn default() -> Self {
        Self::memory()
    }
}

impl SqliteEngine {
    pub fn new(path: Option<String>) -> Self {
        Self::new_with_tables(path, Vec::new())
    }

    pub fn new_with_tables(path: Option<String>, tables: Vec<String>) -> Self {
        match path {
            Some(path) if !path.trim().is_empty() => Self { path, tables },
            _ => Self {
                path: ":memory:".to_string(),
                tables,
            },
        }
    }

    pub fn memory() -> Self {
        Self {
            path: ":memory:".to_string(),
            tables: Vec::new(),
        }
    }

    pub fn path(&self) -> &str {
        &self.path
    }
}

impl EnginePort for SqliteEngine {
    fn kind(&self) -> &str {
        "sqlite"
    }

    fn open(&self) -> PortResult<Box<dyn SessionPort>> {
        SqliteSession::new(self.path.clone(), self.tables.clone())
            .map(|session| Box::new(session) as Box<dyn SessionPort>)
    }
}
