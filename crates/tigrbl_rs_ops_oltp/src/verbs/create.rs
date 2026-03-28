use crate::verbs::NativeOltpVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct CreateVerb;

impl NativeOltpVerb for CreateVerb {
    fn name(&self) -> &'static str {
        "create"
    }

    fn kind(&self) -> tigrbl_rs_spec::op::OpKind {
        tigrbl_rs_spec::op::OpKind::Create
    }
}
