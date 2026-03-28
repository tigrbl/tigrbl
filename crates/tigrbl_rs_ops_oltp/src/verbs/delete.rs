use crate::verbs::NativeOltpVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct DeleteVerb;

impl NativeOltpVerb for DeleteVerb {
    fn name(&self) -> &'static str {
        "delete"
    }

    fn kind(&self) -> tigrbl_rs_spec::op::OpKind {
        tigrbl_rs_spec::op::OpKind::Delete
    }
}
