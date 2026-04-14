use crate::{config::RuntimeConfig, handle::runtime_handle::RuntimeHandle};
use tigrbl_rs_kernel::plan::models::KernelPlan;

#[derive(Debug, Clone, Default)]
pub struct RustRuntime {
    pub config: RuntimeConfig,
}

impl RustRuntime {
    pub fn new(config: RuntimeConfig) -> Self {
        Self { config }
    }

    pub fn instantiate(&self, plan: KernelPlan) -> RuntimeHandle {
        RuntimeHandle::new(plan)
    }
}
