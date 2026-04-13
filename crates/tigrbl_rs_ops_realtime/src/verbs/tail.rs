use crate::verbs::NativeRealtimeVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct TailVerb;

impl NativeRealtimeVerb for TailVerb {
    fn name(&self) -> &'static str {
        "tail"
    }

    fn kind(&self) -> tigrbl_rs_spec::op::OpKind {
        tigrbl_rs_spec::op::OpKind::Tail
    }
}
