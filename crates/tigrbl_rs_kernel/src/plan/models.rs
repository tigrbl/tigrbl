use crate::plan::packed::PackedPlan;
use tigrbl_rs_spec::{Exchange, OpKind, TxScope, Value};

#[derive(Debug, Clone, Default, PartialEq)]
pub struct PlanBinding {
    pub alias: String,
    pub op_name: String,
    pub op_kind: OpKind,
    pub transport: String,
    pub family: String,
    pub framing: Option<String>,
    pub path: String,
    pub method: String,
    pub method_name: String,
    pub exchange: Exchange,
    pub tx_scope: TxScope,
    pub subevents: Vec<String>,
    pub hooks: Vec<String>,
    pub callback_fences: Vec<String>,
    pub table: String,
    pub engine_kind: String,
    pub engine_language: String,
    pub engine_callback: Option<String>,
    pub engine_options: Value,
}

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct PlanRoute {
    pub transport: String,
    pub family: String,
    pub path: String,
    pub method: String,
    pub method_name: String,
    pub binding_alias: String,
    pub op_name: String,
}

#[derive(Debug, Clone, Default, PartialEq)]
pub struct KernelPlan {
    pub app_name: String,
    pub title: String,
    pub version: String,
    pub bindings: Vec<PlanBinding>,
    pub routes: Vec<PlanRoute>,
    pub engine_kind: String,
    pub engine_options: Value,
    pub callbacks: Vec<String>,
    pub runtime: Value,
    pub metadata: Value,
    pub packed: Option<PackedPlan>,
}
