use crate::verbs::NativeOltpVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct MergeVerb;

impl NativeOltpVerb for MergeVerb {
    fn name(&self) -> &'static str {
        "merge"
    }

    fn kind(&self) -> tigrbl_rs_spec::op::OpKind {
        tigrbl_rs_spec::op::OpKind::Merge
    }
}
