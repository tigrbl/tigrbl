use crate::verbs::NativeOlapVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct GroupByVerb;

impl NativeOlapVerb for GroupByVerb {
    fn name(&self) -> &'static str {
        "group_by"
    }

    fn kind(&self) -> tigrbl_rs_spec::op::OpKind {
        tigrbl_rs_spec::op::OpKind::GroupBy
    }
}
