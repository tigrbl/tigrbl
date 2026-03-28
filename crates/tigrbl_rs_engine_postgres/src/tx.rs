use tigrbl_rs_ports::{errors::PortResult, transactions::TransactionPort};

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct PostgresTransaction;

impl TransactionPort for PostgresTransaction {
    fn commit(&self) -> PortResult<()> {
        Ok(())
    }

    fn rollback(&self) -> PortResult<()> {
        Ok(())
    }
}
