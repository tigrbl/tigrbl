use crate::plan::{KernelPlan, PackedPlan, PlanBinding};
use tigrbl_rs_spec::app::AppSpec;

#[derive(Debug, Clone, Default)]
pub struct KernelCompiler;

impl KernelCompiler {
    pub fn compile(&self, app: &AppSpec) -> KernelPlan {
        let bindings = app
            .bindings
            .iter()
            .map(|binding| PlanBinding {
                alias: binding.alias.clone(),
                op_name: binding.op.name.clone(),
            })
            .collect::<Vec<_>>();

        KernelPlan {
            app_name: app.name.clone(),
            packed: Some(PackedPlan::from_binding_count(bindings.len())),
            bindings,
        }
    }
}
