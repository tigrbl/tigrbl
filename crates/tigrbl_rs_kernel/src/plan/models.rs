use crate::plan::packed::PackedPlan;
use tigrbl_rs_spec::OpKind;

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct PlanBinding {
    pub alias: String,
    pub op_name: String,
    pub op_kind: OpKind,
    pub transport: String,
    pub path: String,
    pub table: String,
    pub engine_kind: String,
}

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct PlanRoute {
    pub transport: String,
    pub path: String,
    pub binding_alias: String,
    pub op_name: String,
}

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct KernelPlan {
    pub app_name: String,
    pub bindings: Vec<PlanBinding>,
    pub routes: Vec<PlanRoute>,
    pub engine_kind: String,
    pub packed: Option<PackedPlan>,
}
