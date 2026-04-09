use crate::verbs::NativeOlapVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct AggregateVerb;

impl NativeOlapVerb for AggregateVerb {
    fn name(&self) -> &'static str {
        "aggregate"
    }

    fn kind(&self) -> tigrbl_rs_spec::op::OpKind {
        tigrbl_rs_spec::op::OpKind::Aggregate
    }
}
