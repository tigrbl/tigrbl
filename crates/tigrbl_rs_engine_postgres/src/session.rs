use tigrbl_rs_ports::{errors::PortResult, sessions::SessionPort, transactions::TransactionPort};

use crate::tx::PostgresTransaction;

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct PostgresSession;

impl SessionPort for PostgresSession {
    fn begin(&self) -> PortResult<Box<dyn TransactionPort>> {
        Ok(Box::new(PostgresTransaction::default()))
    }
}
