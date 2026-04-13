use crate::errors::{PortError, PortResult};
use tigrbl_rs_spec::{request::RequestEnvelope, response::ResponseEnvelope};

pub trait TransactionPort: Send + Sync {
    fn commit(&self) -> PortResult<()>;
    fn rollback(&self) -> PortResult<()>;

    fn execute(
        &self,
        table: &str,
        operation: &str,
        kind: &str,
        request: &RequestEnvelope,
    ) -> PortResult<ResponseEnvelope> {
        let _ = (table, operation, request);
        Err(PortError::not_implemented(kind))
    }
}
