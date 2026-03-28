use crate::{config::RuntimeConfig, handle::runtime_handle::RuntimeHandle};
use tigrbl_rs_kernel::plan::models::KernelPlan;

#[derive(Debug, Clone, Default)]
pub struct NativeRuntime {
    pub config: RuntimeConfig,
}

impl NativeRuntime {
    pub fn new(config: RuntimeConfig) -> Self {
        Self { config }
    }

    pub fn instantiate(&self, plan: KernelPlan) -> RuntimeHandle {
        RuntimeHandle::new(plan)
    }
}
