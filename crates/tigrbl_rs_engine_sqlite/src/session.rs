use tigrbl_rs_ports::{errors::PortResult, sessions::SessionPort, transactions::TransactionPort};

use crate::tx::{initialize_schema, SqliteTransaction};

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct SqliteSession {
    path: String,
}

impl SqliteSession {
    pub fn new(path: String) -> PortResult<Self> {
        initialize_schema(&path)?;
        Ok(Self { path })
    }
}

impl SessionPort for SqliteSession {
    fn begin(&self) -> PortResult<Box<dyn TransactionPort>> {
        SqliteTransaction::begin(self.path.clone())
            .map(|tx| Box::new(tx) as Box<dyn TransactionPort>)
    }
}
