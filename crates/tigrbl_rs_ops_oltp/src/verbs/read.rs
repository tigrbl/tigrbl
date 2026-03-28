use crate::verbs::NativeOltpVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct ReadVerb;

impl NativeOltpVerb for ReadVerb {
    fn name(&self) -> &'static str {
        "read"
    }

    fn kind(&self) -> tigrbl_rs_spec::op::OpKind {
        tigrbl_rs_spec::op::OpKind::Read
    }
}
