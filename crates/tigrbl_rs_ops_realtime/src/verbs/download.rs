use crate::verbs::NativeRealtimeVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct DownloadVerb;

impl NativeRealtimeVerb for DownloadVerb {
    fn name(&self) -> &'static str {
        "download"
    }

    fn kind(&self) -> tigrbl_rs_spec::op::OpKind {
        tigrbl_rs_spec::op::OpKind::Download
    }
}
