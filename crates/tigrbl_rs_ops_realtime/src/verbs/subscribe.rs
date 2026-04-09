use crate::verbs::NativeRealtimeVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct SubscribeVerb;

impl NativeRealtimeVerb for SubscribeVerb {
    fn name(&self) -> &'static str {
        "subscribe"
    }

    fn kind(&self) -> tigrbl_rs_spec::op::OpKind {
        tigrbl_rs_spec::op::OpKind::Subscribe
    }
}
