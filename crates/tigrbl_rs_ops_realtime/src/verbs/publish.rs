use crate::verbs::NativeRealtimeVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct PublishVerb;

impl NativeRealtimeVerb for PublishVerb {
    fn name(&self) -> &'static str {
        "publish"
    }

    fn kind(&self) -> tigrbl_rs_spec::op::OpKind {
        tigrbl_rs_spec::op::OpKind::Publish
    }
}
