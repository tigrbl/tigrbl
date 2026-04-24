use tigrbl_rs_ports::{errors::PortResult, sessions::SessionPort, transactions::TransactionPort};

use crate::tx::SqliteTransaction;

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct SqliteSession {
    path: String,
}

impl SqliteSession {
    pub fn new(path: String) -> Self {
        Self { path }
    }
}

impl SessionPort for SqliteSession {
    fn begin(&self) -> PortResult<Box<dyn TransactionPort>> {
        SqliteTransaction::begin(self.path.clone())
            .map(|tx| Box::new(tx) as Box<dyn TransactionPort>)
    }
}
