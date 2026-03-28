use crate::errors::NativeResult;
use tigrbl_rs_kernel::KernelCompiler;
use tigrbl_rs_runtime::{NativeRuntime, RuntimeConfig};
use tigrbl_rs_spec::app::AppSpec;

#[derive(Debug, Clone)]
pub struct RuntimeHandle {
    pub description: String,
}

impl RuntimeHandle {
    pub fn describe(&self) -> String {
        self.description.clone()
    }
}

pub fn create_runtime_handle(spec_json: &str) -> NativeResult<RuntimeHandle> {
    let _ = spec_json;
    let compiler = KernelCompiler::default();
    let plan = compiler.compile(&AppSpec::default());
    let runtime = NativeRuntime::new(RuntimeConfig::default());
    let handle = runtime.instantiate(plan);
    Ok(RuntimeHandle {
        description: handle.description,
    })
}
