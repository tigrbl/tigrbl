use crate::verbs::NativeOltpVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct ListVerb;

impl NativeOltpVerb for ListVerb {
    fn name(&self) -> &'static str {
        "list"
    }

    fn kind(&self) -> tigrbl_rs_spec::op::OpKind {
        tigrbl_rs_spec::op::OpKind::List
    }
}
