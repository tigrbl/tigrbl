use crate::errors::PortResult;
use tigrbl_rs_spec::values::Value;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ChannelFamily {
    Request,
    Response,
    Stream,
    Socket,
    Session,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ChannelSubevent {
    Connect,
    Receive,
    Emit,
    Complete,
    Disconnect,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct OpChannel {
    pub kind: String,
    pub family: ChannelFamily,
    pub exchange: String,
    pub protocol: String,
    pub path: String,
    pub selector: Option<String>,
    pub framing: Option<String>,
    pub subevents: Vec<ChannelSubevent>,
}

pub trait ChannelPort: Send + Sync {
    fn receive(&self, channel: &OpChannel) -> PortResult<Option<Value>>;
    fn emit(&self, channel: &OpChannel, payload: Value) -> PortResult<()>;
    fn complete(&self, channel: &OpChannel) -> PortResult<()>;
}
