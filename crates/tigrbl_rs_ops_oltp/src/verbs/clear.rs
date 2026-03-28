use crate::verbs::NativeOltpVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct ClearVerb;

impl NativeOltpVerb for ClearVerb {
    fn name(&self) -> &'static str {
        "clear"
    }

    fn kind(&self) -> tigrbl_rs_spec::op::OpKind {
        tigrbl_rs_spec::op::OpKind::Clear
    }
}
