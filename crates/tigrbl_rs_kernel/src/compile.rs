use crate::plan::{KernelPlan, PackedPlan, PlanBinding, PlanRoute};
use tigrbl_rs_spec::app::AppSpec;

#[derive(Debug, Clone, Default)]
pub struct KernelCompiler;

impl KernelCompiler {
    pub fn compile(&self, app: &AppSpec) -> KernelPlan {
        let default_engine = app
            .engines
            .first()
            .map(|engine| engine.kind.clone())
            .unwrap_or_else(|| "inmemory".to_string());

        let bindings = app
            .bindings
            .iter()
            .map(|binding| PlanBinding {
                alias: binding.alias.clone(),
                op_name: binding.op.name.clone(),
                op_kind: binding.op.kind.clone(),
                transport: binding.transport.clone(),
                path: binding
                    .op
                    .route
                    .clone()
                    .or_else(|| binding.path.clone())
                    .unwrap_or_else(|| format!("/{}", binding.alias)),
                table: binding
                    .table
                    .as_ref()
                    .map(|table| table.name.clone())
                    .unwrap_or_else(|| binding.alias.clone()),
                engine_kind: default_engine.clone(),
            })
            .collect::<Vec<_>>();
        let routes = bindings
            .iter()
            .map(|binding| PlanRoute {
                transport: binding.transport.clone(),
                path: binding.path.clone(),
                binding_alias: binding.alias.clone(),
                op_name: binding.op_name.clone(),
            })
            .collect::<Vec<_>>();

        KernelPlan {
            app_name: app.name.clone(),
            bindings,
            routes,
            engine_kind: default_engine,
            packed: Some(PackedPlan::from_binding_count(app.bindings.len())),
        }
    }
}
