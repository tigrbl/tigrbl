use crate::verbs::NativeOltpVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct CountVerb;

impl NativeOltpVerb for CountVerb {
    fn name(&self) -> &'static str {
        "count"
    }

    fn kind(&self) -> tigrbl_rs_spec::op::OpKind {
        tigrbl_rs_spec::op::OpKind::Count
    }
}
