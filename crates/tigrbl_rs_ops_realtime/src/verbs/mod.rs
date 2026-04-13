pub mod append_chunk;
pub mod checkpoint;
pub mod download;
pub mod publish;
pub mod send_datagram;
pub mod subscribe;
pub mod tail;
pub mod upload;

pub trait NativeRealtimeVerb {
    fn name(&self) -> &'static str;
    fn kind(&self) -> tigrbl_rs_spec::op::OpKind;
}
