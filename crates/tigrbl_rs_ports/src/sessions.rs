use crate::{errors::PortResult, transactions::TransactionPort};

pub trait SessionPort: Send + Sync {
    fn begin(&self) -> PortResult<Box<dyn TransactionPort>>;
    fn read_only(&self) -> bool {
        false
    }
}
