use crate::verbs::NativeRealtimeVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct UploadVerb;

impl NativeRealtimeVerb for UploadVerb {
    fn name(&self) -> &'static str {
        "upload"
    }

    fn kind(&self) -> tigrbl_rs_spec::op::OpKind {
        tigrbl_rs_spec::op::OpKind::Upload
    }
}
