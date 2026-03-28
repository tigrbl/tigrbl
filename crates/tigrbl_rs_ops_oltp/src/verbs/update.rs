use crate::verbs::NativeOltpVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct UpdateVerb;

impl NativeOltpVerb for UpdateVerb {
    fn name(&self) -> &'static str {
        "update"
    }

    fn kind(&self) -> tigrbl_rs_spec::op::OpKind {
        tigrbl_rs_spec::op::OpKind::Update
    }
}
