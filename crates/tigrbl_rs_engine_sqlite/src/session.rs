use tigrbl_rs_ports::{errors::PortResult, sessions::SessionPort, transactions::TransactionPort};

use crate::tx::SqliteTransaction;

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct SqliteSession;

impl SessionPort for SqliteSession {
    fn begin(&self) -> PortResult<Box<dyn TransactionPort>> {
        Ok(Box::new(SqliteTransaction::default()))
    }
}
