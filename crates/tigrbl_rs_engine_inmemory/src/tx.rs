use tigrbl_rs_ports::{errors::PortResult, transactions::TransactionPort};

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct InmemoryTransaction;

impl TransactionPort for InmemoryTransaction {
    fn commit(&self) -> PortResult<()> {
        Ok(())
    }

    fn rollback(&self) -> PortResult<()> {
        Ok(())
    }
}
