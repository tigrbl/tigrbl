use std::sync::{Arc, Mutex};

use tigrbl_rs_ports::{errors::PortResult, sessions::SessionPort, transactions::TransactionPort};

use crate::tx::InmemoryTransaction;

#[derive(Debug, Clone, Default)]
pub struct InmemorySession {
    pub(crate) shared: Arc<Mutex<crate::tx::Store>>,
}

impl InmemorySession {
    pub fn new(shared: Arc<Mutex<crate::tx::Store>>) -> Self {
        Self { shared }
    }
}

impl SessionPort for InmemorySession {
    fn begin(&self) -> PortResult<Box<dyn TransactionPort>> {
        Ok(Box::new(InmemoryTransaction::new(self.shared.clone())))
    }
}
