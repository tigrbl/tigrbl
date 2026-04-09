use crate::verbs::NativeRealtimeVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct AppendChunkVerb;

impl NativeRealtimeVerb for AppendChunkVerb {
    fn name(&self) -> &'static str {
        "append_chunk"
    }

    fn kind(&self) -> tigrbl_rs_spec::op::OpKind {
        tigrbl_rs_spec::op::OpKind::AppendChunk
    }
}
