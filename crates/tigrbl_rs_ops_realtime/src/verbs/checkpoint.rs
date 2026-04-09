use crate::verbs::NativeRealtimeVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct CheckpointVerb;

impl NativeRealtimeVerb for CheckpointVerb {
    fn name(&self) -> &'static str {
        "checkpoint"
    }

    fn kind(&self) -> tigrbl_rs_spec::op::OpKind {
        tigrbl_rs_spec::op::OpKind::Checkpoint
    }
}
