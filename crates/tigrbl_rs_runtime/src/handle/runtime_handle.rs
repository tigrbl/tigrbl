use tigrbl_rs_kernel::plan::models::KernelPlan;

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct RuntimeHandle {
    pub description: String,
    pub plan: KernelPlan,
}

impl RuntimeHandle {
    pub fn new(plan: KernelPlan) -> Self {
        let description = format!(
            "runtime handle for {} binding(s) in app {}",
            plan.bindings.len(),
            plan.app_name
        );
        Self { description, plan }
    }
}
