use std::collections::BTreeMap;

use crate::plan::{KernelPlan, PackedPlan};
use tigrbl_rs_spec::{AppSpec, BindingSpec, Exchange, TxScope};

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct RouteSnapshot {
    pub alias: String,
    pub target: String,
    pub route: Option<String>,
    pub transport: String,
    pub exchange: String,
    pub family: String,
}

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct OpViewSnapshot {
    pub alias: String,
    pub target: String,
    pub route: Option<String>,
    pub exchange: String,
    pub tx_scope: String,
    pub family: String,
    pub subevents: Vec<String>,
    pub hook_count: usize,
}

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct DocsSnapshot {
    pub openapi_paths: Vec<String>,
    pub openrpc_methods: Vec<String>,
    pub asyncapi_channels: Vec<String>,
}

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct KernelParitySnapshot {
    pub app_name: String,
    pub routes: Vec<RouteSnapshot>,
    pub opviews: Vec<OpViewSnapshot>,
    pub phase_plans: BTreeMap<String, Vec<String>>,
    pub packed_plan: PackedPlan,
    pub docs: DocsSnapshot,
}

fn phase_plan(binding: &BindingSpec) -> Vec<String> {
    let mut phases = vec![
        "INGRESS_BEGIN".to_string(),
        "INGRESS_DISPATCH".to_string(),
        "PRE_HANDLER".to_string(),
        "HANDLER".to_string(),
        "POST_HANDLER".to_string(),
    ];
    if binding.op.tx_scope != TxScope::None {
        phases.insert(2, "START_TX".to_string());
        phases.push("TX_COMMIT".to_string());
    }
    if binding.transport == "sse"
        || binding.transport == "ws"
        || binding.transport == "wss"
        || binding.transport == "webtransport"
        || binding.op.exchange != Exchange::RequestResponse
    {
        phases.push("POST_EMIT".to_string());
    }
    phases.push("POST_RESPONSE".to_string());
    phases
}

pub fn build_parity_snapshot(app: &AppSpec, plan: &KernelPlan) -> KernelParitySnapshot {
    let mut routes = Vec::new();
    let mut opviews = Vec::new();
    let mut phase_plans = BTreeMap::new();
    let mut openapi_paths = Vec::new();
    let mut openrpc_methods = Vec::new();
    let mut asyncapi_channels = Vec::new();

    for binding in &app.bindings {
        let route = binding.path.clone().or_else(|| binding.op.route.clone());
        let transport = if binding.transport.is_empty() {
            "rest".to_string()
        } else {
            binding.transport.clone()
        };
        let exchange = binding.op.exchange.as_str().to_string();
        let family = if binding.family.is_empty() {
            if transport == "ws" || transport == "wss" || transport == "webtransport" {
                "bidirectional".to_string()
            } else if exchange == "server_stream" {
                "server_stream".to_string()
            } else {
                "request_response".to_string()
            }
        } else {
            binding.family.clone()
        };

        routes.push(RouteSnapshot {
            alias: binding.alias.clone(),
            target: binding.op.kind.as_str().to_string(),
            route: route.clone(),
            transport: transport.clone(),
            exchange: exchange.clone(),
            family: family.clone(),
        });
        opviews.push(OpViewSnapshot {
            alias: binding.alias.clone(),
            target: binding.op.kind.as_str().to_string(),
            route: route.clone(),
            exchange: exchange.clone(),
            tx_scope: binding.op.tx_scope.as_str().to_string(),
            family,
            subevents: binding.op.subevents.clone(),
            hook_count: binding.hooks.len(),
        });
        phase_plans.insert(binding.alias.clone(), phase_plan(binding));

        if let Some(path) = route.clone() {
            if exchange == "request_response" && (transport == "rest" || transport == "jsonrpc") {
                openapi_paths.push(path.clone());
            }
            if exchange != "request_response" {
                asyncapi_channels.push(path);
            }
        } else if exchange != "request_response" {
            asyncapi_channels.push(binding.alias.clone());
        }
        openrpc_methods.push(binding.alias.clone());
    }

    KernelParitySnapshot {
        app_name: app.name.clone(),
        routes,
        opviews,
        phase_plans,
        packed_plan: plan.packed.clone().unwrap_or_default(),
        docs: DocsSnapshot {
            openapi_paths,
            openrpc_methods,
            asyncapi_channels,
        },
    }
}
