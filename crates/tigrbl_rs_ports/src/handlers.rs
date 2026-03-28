use crate::errors::PortResult;
use tigrbl_rs_spec::{request::RequestEnvelope, response::ResponseEnvelope};

pub trait HandlerPort: Send + Sync {
    fn name(&self) -> &str;
    fn handle(&self, request: &RequestEnvelope) -> PortResult<ResponseEnvelope>;
}
