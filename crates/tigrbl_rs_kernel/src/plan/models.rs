use crate::plan::packed::PackedPlan;

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct PlanBinding {
    pub alias: String,
    pub op_name: String,
}

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct KernelPlan {
    pub app_name: String,
    pub bindings: Vec<PlanBinding>,
    pub packed: Option<PackedPlan>,
}
