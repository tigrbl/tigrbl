use crate::errors::NativeResult;
use serde_json::{json, Value as JsonValue};
use tigrbl_rs_kernel::KernelCompiler;
use tigrbl_rs_runtime::{NativeRuntime, RuntimeConfig};
use tigrbl_rs_spec::{
    request::RequestEnvelope, response::ResponseEnvelope, serde::json as spec_json,
};

pub struct RuntimeHandle {
    handle: tigrbl_rs_runtime::RuntimeHandle,
}

impl RuntimeHandle {
    pub fn describe(&self) -> String {
        self.handle.describe()
    }

    pub fn execute_rest_json(&self, request_json: &str) -> NativeResult<String> {
        let request = decode_request(request_json)?;
        let response = self
            .handle
            .execute_rest(request)
            .map_err(|err| err.to_string())?;
        encode_response(&response)
    }

    pub fn execute_jsonrpc_json(&self, request_json: &str) -> NativeResult<String> {
        let request = decode_request(request_json)?;
        let response = self
            .handle
            .execute_jsonrpc(request)
            .map_err(|err| err.to_string())?;
        encode_response(&response)
    }

    pub fn plan_json(&self) -> NativeResult<String> {
        let plan = &self.handle.plan;
        serde_json::to_string(&json!({
            "app_name": plan.app_name,
            "engine_kind": plan.engine_kind,
            "bindings": plan.bindings.iter().map(|binding| {
                json!({
                    "alias": binding.alias,
                    "op_name": binding.op_name,
                    "op_kind": binding.op_kind.as_str(),
                    "transport": binding.transport,
                    "path": binding.path,
                    "table": binding.table,
                    "engine_kind": binding.engine_kind,
                })
            }).collect::<Vec<_>>(),
            "routes": plan.routes.iter().map(|route| {
                json!({
                    "transport": route.transport,
                    "path": route.path,
                    "binding_alias": route.binding_alias,
                    "op_name": route.op_name,
                })
            }).collect::<Vec<_>>(),
            "packed": plan.packed.as_ref().map(|packed| json!({
                "segments": packed.segments,
                "hot_paths": packed.hot_paths,
                "fused_steps": packed.fused_steps,
                "routes": packed.routes,
            })),
        }))
        .map_err(|err| err.to_string())
    }
}

pub fn create_runtime_handle(spec_json: &str) -> NativeResult<RuntimeHandle> {
    let spec = crate::spec_codec::decode_spec(spec_json)?;
    let compiler = KernelCompiler::default();
    let plan = compiler.compile(&spec);
    let runtime = NativeRuntime::new(RuntimeConfig::default());
    Ok(RuntimeHandle {
        handle: runtime.instantiate(plan),
    })
}

fn decode_request(raw: &str) -> NativeResult<RequestEnvelope> {
    spec_json::request_from_json(raw).map_err(|err| err.to_string())
}

fn encode_response(response: &ResponseEnvelope) -> NativeResult<String> {
    spec_json::response_to_json(response).map_err(|err| err.to_string())
}

#[allow(dead_code)]
fn _json_value(raw: &str) -> NativeResult<JsonValue> {
    serde_json::from_str(raw).map_err(|err| err.to_string())
}
