use crate::plan::{KernelPlan, PackedPlan, PlanBinding, PlanRoute};
use tigrbl_rs_spec::app::AppSpec;
use tigrbl_rs_spec::{BindingSpec, Exchange, OpKind, OpSpec, TableSpec, TxScope};

const DEFAULT_ROOT_ALIAS: &str = "__tigrbl_default_root__";
const DEFAULT_ROOT_PATH: &str = "/";

#[derive(Debug, Clone, Default)]
pub struct KernelCompiler;

impl KernelCompiler {
    pub fn compile(&self, app: &AppSpec) -> KernelPlan {
        let default_engine = app.engines.first().cloned();
        let default_engine_kind = default_engine
            .as_ref()
            .map(|engine| engine.kind.clone())
            .unwrap_or_else(|| "inmemory".to_string());
        let default_engine_language = default_engine
            .as_ref()
            .map(|engine| engine.language.clone())
            .unwrap_or_else(|| "rust".to_string());
        let default_engine_options = default_engine
            .as_ref()
            .map(|engine| tigrbl_rs_spec::Value::Object(engine.options.clone()))
            .unwrap_or(tigrbl_rs_spec::Value::Null);
        let default_engine_callback = default_engine.and_then(|engine| engine.callback);
        let mut source_bindings = app.bindings.clone();
        if !has_root_binding(&source_bindings) {
            source_bindings.push(default_root_binding());
        }

        let bindings = source_bindings
            .iter()
            .map(|binding| PlanBinding {
                alias: binding.alias.clone(),
                op_name: binding.op.name.clone(),
                op_kind: binding.op.kind.clone(),
                transport: binding.transport.clone(),
                family: binding.family.clone(),
                framing: binding.framing.clone(),
                path: binding
                    .op
                    .route
                    .clone()
                    .or_else(|| binding.path.clone())
                    .unwrap_or_else(|| format!("/{}", binding.alias)),
                method: route_method(&binding.transport, binding.op.kind.as_str()),
                method_name: route_method_name(&binding.transport, binding),
                exchange: binding.op.exchange.clone(),
                tx_scope: binding.op.tx_scope.clone(),
                subevents: binding.op.subevents.clone(),
                hooks: binding.hooks.iter().map(|hook| hook.name.clone()).collect(),
                callback_fences: binding
                    .hooks
                    .iter()
                    .map(|hook| format!("hook:{}", hook.name))
                    .collect(),
                table: binding
                    .table
                    .as_ref()
                    .map(|table| table.name.clone())
                    .unwrap_or_else(|| binding.alias.clone()),
                engine_kind: default_engine_kind.clone(),
                engine_language: default_engine_language.clone(),
                engine_callback: default_engine_callback.clone(),
                engine_options: default_engine_options.clone(),
            })
            .collect::<Vec<_>>();
        let routes = bindings
            .iter()
            .map(|binding| PlanRoute {
                transport: binding.transport.clone(),
                family: binding.family.clone(),
                path: binding.path.clone(),
                method: binding.method.clone(),
                method_name: binding.method_name.clone(),
                binding_alias: binding.alias.clone(),
                op_name: binding.op_name.clone(),
            })
            .collect::<Vec<_>>();

        KernelPlan {
            app_name: app.name.clone(),
            title: app.title.clone(),
            version: app.version.clone(),
            bindings,
            routes,
            engine_kind: default_engine_kind,
            engine_options: default_engine_options,
            callbacks: app
                .callbacks
                .iter()
                .map(|callback| callback.name.clone())
                .collect(),
            runtime: tigrbl_rs_spec::Value::Object(app.runtime.clone()),
            metadata: tigrbl_rs_spec::Value::Object(
                app.metadata
                    .iter()
                    .map(|(key, value)| (key.clone(), tigrbl_rs_spec::Value::String(value.clone())))
                    .collect(),
            ),
            packed: Some(PackedPlan::from_binding_count(source_bindings.len())),
        }
    }
}

fn has_root_binding(bindings: &[BindingSpec]) -> bool {
    bindings.iter().any(is_root_binding)
}

fn is_root_binding(binding: &BindingSpec) -> bool {
    binding.transport == "rest" && normalize_path(binding_path(binding)) == "/"
}

fn binding_path(binding: &BindingSpec) -> String {
    binding
        .path
        .clone()
        .or_else(|| binding.op.route.clone())
        .unwrap_or_else(|| format!("/{}", binding.alias))
}

fn default_root_binding() -> BindingSpec {
    BindingSpec {
        alias: DEFAULT_ROOT_ALIAS.to_string(),
        transport: "rest".to_string(),
        path: Some(DEFAULT_ROOT_PATH.to_string()),
        family: "rest".to_string(),
        framing: None,
        op: OpSpec {
            kind: OpKind::Read,
            name: DEFAULT_ROOT_ALIAS.to_string(),
            route: Some(DEFAULT_ROOT_PATH.to_string()),
            exchange: Exchange::RequestResponse,
            tx_scope: TxScope::Inherit,
            subevents: vec![],
        },
        table: Some(TableSpec {
            name: DEFAULT_ROOT_ALIAS.to_string(),
            columns: vec![],
        }),
        hooks: vec![],
    }
}

fn normalize_path(path: String) -> String {
    let trimmed = path.trim_end_matches('/');
    if trimmed.is_empty() {
        "/".to_string()
    } else {
        trimmed.to_string()
    }
}

fn route_method(transport: &str, op_kind: &str) -> String {
    match transport {
        "rest" => match op_kind {
            "create" | "bulk_create" => "POST",
            "read" | "list" | "count" | "exists" => "GET",
            "delete" | "bulk_delete" => "DELETE",
            "replace" | "bulk_replace" => "PUT",
            "update" | "merge" | "bulk_update" | "bulk_merge" => "PATCH",
            _ => "POST",
        },
        "jsonrpc" => "POST",
        "ws" | "wss" | "websocket" => "MESSAGE",
        "sse" | "stream" | "streaming" => "GET",
        _ => "POST",
    }
    .to_string()
}

fn route_method_name(transport: &str, binding: &tigrbl_rs_spec::BindingSpec) -> String {
    if transport == "jsonrpc" {
        return binding.alias.clone();
    }
    binding.op.name.clone()
}
