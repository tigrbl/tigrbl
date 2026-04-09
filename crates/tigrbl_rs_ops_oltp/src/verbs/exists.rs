use crate::verbs::NativeOltpVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct ExistsVerb;

impl NativeOltpVerb for ExistsVerb {
    fn name(&self) -> &'static str {
        "exists"
    }

    fn kind(&self) -> tigrbl_rs_spec::op::OpKind {
        tigrbl_rs_spec::op::OpKind::Exists
    }
}
