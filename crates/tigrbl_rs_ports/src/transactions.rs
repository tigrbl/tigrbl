use crate::errors::PortResult;

pub trait TransactionPort: Send + Sync {
    fn commit(&self) -> PortResult<()>;
    fn rollback(&self) -> PortResult<()>;
}
