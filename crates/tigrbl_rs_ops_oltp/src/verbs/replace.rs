use crate::verbs::NativeOltpVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct ReplaceVerb;

impl NativeOltpVerb for ReplaceVerb {
    fn name(&self) -> &'static str {
        "replace"
    }

    fn kind(&self) -> tigrbl_rs_spec::op::OpKind {
        tigrbl_rs_spec::op::OpKind::Replace
    }
}
