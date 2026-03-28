use tigrbl_rs_ports::{errors::PortResult, sessions::SessionPort, transactions::TransactionPort};

use crate::tx::InmemoryTransaction;

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct InmemorySession;

impl SessionPort for InmemorySession {
    fn begin(&self) -> PortResult<Box<dyn TransactionPort>> {
        Ok(Box::new(InmemoryTransaction::default()))
    }
}
