use crate::verbs::NativeRealtimeVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct SendDatagramVerb;

impl NativeRealtimeVerb for SendDatagramVerb {
    fn name(&self) -> &'static str {
        "send_datagram"
    }

    fn kind(&self) -> tigrbl_rs_spec::op::OpKind {
        tigrbl_rs_spec::op::OpKind::SendDatagram
    }
}
