use crate::errors::RustResult;
use pyo3::prelude::*;
use serde_json::{json, Map, Value as JsonValue};
use tigrbl_rs_kernel::KernelPlan;
use tigrbl_rs_runtime::{RuntimeConfig, RustRuntime};
use tigrbl_rs_spec::{
    request::RequestEnvelope, response::ResponseEnvelope, serde::json as spec_json, Exchange,
    OpKind, TxScope, Value,
};

pub struct RuntimeHandle {
    handle: tigrbl_rs_runtime::RuntimeHandle,
}

#[pyclass(name = "RuntimeHandle", unsendable)]
pub struct PyRuntimeHandle {
    inner: RuntimeHandle,
}

impl From<RuntimeHandle> for PyRuntimeHandle {
    fn from(value: RuntimeHandle) -> Self {
        Self { inner: value }
    }
}

#[pymethods]
impl PyRuntimeHandle {
    fn describe(&self) -> PyResult<String> {
        Ok(self.inner.describe())
    }

    fn execute_rest_json(&self, request_json: &str) -> PyResult<String> {
        self.inner
            .execute_rest_json(request_json)
            .map_err(pyo3::exceptions::PyRuntimeError::new_err)
    }

    fn execute_jsonrpc_json(&self, request_json: &str) -> PyResult<String> {
        self.inner
            .execute_jsonrpc_json(request_json)
            .map_err(pyo3::exceptions::PyRuntimeError::new_err)
    }

    fn execute_ws_json(&self, request_json: &str) -> PyResult<String> {
        self.inner
            .execute_ws_json(request_json)
            .map_err(pyo3::exceptions::PyRuntimeError::new_err)
    }

    fn execute_stream_json(&self, request_json: &str) -> PyResult<String> {
        self.inner
            .execute_stream_json(request_json)
            .map_err(pyo3::exceptions::PyRuntimeError::new_err)
    }

    fn execute_sse_json(&self, request_json: &str) -> PyResult<String> {
        self.inner
            .execute_sse_json(request_json)
            .map_err(pyo3::exceptions::PyRuntimeError::new_err)
    }

    fn plan_json(&self) -> PyResult<String> {
        self.inner
            .plan_json()
            .map_err(pyo3::exceptions::PyRuntimeError::new_err)
    }

    fn begin_request(&self, transport: &str) {
        self.inner.begin_request(transport);
    }

    fn callback_fence(&self, kind: &str, name: &str) {
        self.inner.callback_fence(kind, name);
    }

    fn finish_response(&self, transport: &str) {
        self.inner.finish_response(transport);
    }

    fn ffi_events(&self) -> PyResult<String> {
        serde_json::to_string(&self.inner.ffi_events())
            .map_err(|err| pyo3::exceptions::PyRuntimeError::new_err(err.to_string()))
    }
}

impl RuntimeHandle {
    pub fn describe(&self) -> String {
        self.handle.describe()
    }

    pub fn begin_request(&self, transport: &str) {
        crate::callback_registry::record_event(
            "request_entry",
            serde_json::json!({"transport": transport}),
        );
    }

    pub fn callback_fence(&self, kind: &str, name: &str) {
        crate::callback_registry::record_event(
            "callback_fence_enter",
            serde_json::json!({"kind": kind, "name": name}),
        );
        crate::callback_registry::record_event(
            "callback_fence_exit",
            serde_json::json!({"kind": kind, "name": name}),
        );
    }

    pub fn finish_response(&self, transport: &str) {
        crate::callback_registry::record_event(
            "response_exit",
            serde_json::json!({"transport": transport}),
        );
    }

    pub fn ffi_events(&self) -> Vec<serde_json::Value> {
        crate::callback_registry::ffi_boundary_events()
    }

    pub fn execute_rest_json(&self, request_json: &str) -> RustResult<String> {
        let request = decode_request(request_json)?;
        self.begin_request("rest");
        let response = self
            .handle
            .execute_rest(request)
            .map_err(|err| err.to_string())?;
        self.finish_response("rest");
        encode_response(&response)
    }

    pub fn execute_jsonrpc_json(&self, request_json: &str) -> RustResult<String> {
        let request = decode_request(request_json)?;
        self.begin_request("jsonrpc");
        let response = self
            .handle
            .execute_jsonrpc(request)
            .map_err(|err| err.to_string())?;
        self.finish_response("jsonrpc");
        encode_response(&response)
    }

    pub fn execute_ws_json(&self, request_json: &str) -> RustResult<String> {
        let request = decode_request(request_json)?;
        self.begin_request("ws");
        let response = self
            .handle
            .execute_envelope("ws", request)
            .map_err(|err| err.to_string())?;
        self.finish_response("ws");
        encode_response(&response)
    }

    pub fn execute_stream_json(&self, request_json: &str) -> RustResult<String> {
        let request = decode_request(request_json)?;
        self.begin_request("stream");
        let response = self
            .handle
            .execute_envelope("stream", request)
            .map_err(|err| err.to_string())?;
        self.finish_response("stream");
        encode_response(&response)
    }

    pub fn execute_sse_json(&self, request_json: &str) -> RustResult<String> {
        let request = decode_request(request_json)?;
        self.begin_request("sse");
        let response = self
            .handle
            .execute_envelope("sse", request)
            .map_err(|err| err.to_string())?;
        self.finish_response("sse");
        encode_response(&response)
    }

    pub fn plan_json(&self) -> RustResult<String> {
        encode_plan(&self.handle.plan)
    }
}

pub fn create_runtime_handle(plan_json: &str) -> RustResult<RuntimeHandle> {
    let plan = decode_plan(plan_json)?;
    let runtime = RustRuntime::new(RuntimeConfig::default());
    crate::callback_registry::record_event(
        "create_runtime_handle",
        serde_json::json!({"app_name": plan.app_name}),
    );
    Ok(RuntimeHandle {
        handle: runtime.instantiate(plan),
    })
}

fn decode_request(raw: &str) -> RustResult<RequestEnvelope> {
    spec_json::request_from_json(raw).map_err(|err| err.to_string())
}

fn encode_response(response: &ResponseEnvelope) -> RustResult<String> {
    spec_json::response_to_json(response).map_err(|err| err.to_string())
}

#[allow(dead_code)]
fn _json_value(raw: &str) -> RustResult<JsonValue> {
    serde_json::from_str(raw).map_err(|err| err.to_string())
}

pub fn encode_plan(plan: &KernelPlan) -> RustResult<String> {
    serde_json::to_string(&json!({
        "app_name": plan.app_name,
        "title": plan.title,
        "version": plan.version,
        "engine_kind": plan.engine_kind,
        "engine_options": value_to_json(&plan.engine_options),
        "binding_count": plan.bindings.len(),
        "route_count": plan.routes.len(),
        "callbacks": plan.callbacks,
        "runtime": value_to_json(&plan.runtime),
        "metadata": value_to_json(&plan.metadata),
        "bindings": plan.bindings.iter().map(|binding| {
            json!({
                "alias": binding.alias,
                "op_name": binding.op_name,
                "op_kind": binding.op_kind.as_str(),
                "transport": binding.transport,
                "family": binding.family,
                "framing": binding.framing,
                "path": binding.path,
                "method": binding.method,
                "method_name": binding.method_name,
                "exchange": binding.exchange.as_str(),
                "tx_scope": binding.tx_scope.as_str(),
                "subevents": binding.subevents,
                "hooks": binding.hooks,
                "callback_fences": binding.callback_fences,
                "table": binding.table,
                "engine_kind": binding.engine_kind,
                "engine_language": binding.engine_language,
                "engine_callback": binding.engine_callback,
                "engine_options": value_to_json(&binding.engine_options),
            })
        }).collect::<Vec<_>>(),
        "routes": plan.routes.iter().map(|route| {
            json!({
                "transport": route.transport,
                "family": route.family,
                "path": route.path,
                "method": route.method,
                "method_name": route.method_name,
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

pub fn decode_plan(raw: &str) -> RustResult<KernelPlan> {
    let parsed: JsonValue = serde_json::from_str(raw).map_err(|err| err.to_string())?;
    let object = parsed
        .as_object()
        .ok_or_else(|| "compiled plan payload must be a JSOa object".to_string())?;
    let bindings = array_field(object, "bindings")
        .ok_or_else(|| "compiled plan bindings must be present".to_string())?
        .iter()
        .map(decode_binding)
        .collect::<RustResult<Vec<_>>>()?;
    let routes = array_field(object, "routes")
        .ok_or_else(|| "compiled plan routes must be present".to_string())?
        .iter()
        .map(decode_route)
        .collect::<RustResult<Vec<_>>>()?;
    let packed = object
        .get("packed")
        .and_then(|value| value.as_object())
        .map(|packed| tigrbl_rs_kernel::PackedPlan {
            segments: number_field(packed, "segments").unwrap_or(0),
            hot_paths: number_field(packed, "hot_paths").unwrap_or(0),
            fused_steps: number_field(packed, "fused_steps").unwrap_or(0),
            routes: number_field(packed, "routes").unwrap_or(0),
        });
    Ok(KernelPlan {
        app_name: string_field(object, "app_name").unwrap_or_default(),
        title: string_field(object, "title").unwrap_or_default(),
        version: string_field(object, "version").unwrap_or_default(),
        bindings,
        routes,
        engine_kind: string_field(object, "engine_kind").unwrap_or_else(|| "inmemory".to_string()),
        engine_options: object
            .get("engine_options")
            .map(value_from_json)
            .unwrap_or(Value::Null),
        callbacks: array_field(object, "callbacks")
            .map(string_vec)
            .unwrap_or_default(),
        runtime: object
            .get("runtime")
            .map(value_from_json)
            .unwrap_or(Value::Null),
        metadata: object
            .get("metadata")
            .map(value_from_json)
            .unwrap_or(Value::Null),
        packed,
    })
}

fn decode_binding(value: &JsonValue) -> RustResult<tigrbl_rs_kernel::plan::models::PlanBinding> {
    let object = value
        .as_object()
        .ok_or_else(|| "compiled binding must be a JSOa object".to_string())?;
    Ok(tigrbl_rs_kernel::plan::models::PlanBinding {
        alias: string_field(object, "alias").unwrap_or_default(),
        op_name: string_field(object, "op_name").unwrap_or_default(),
        op_kind: parse_op_kind(string_field(object, "op_kind").as_deref()),
        transport: string_field(object, "transport").unwrap_or_else(|| "rest".to_string()),
        family: string_field(object, "family").unwrap_or_else(|| "rest".to_string()),
        framing: string_field(object, "framing"),
        path: string_field(object, "path").unwrap_or_default(),
        method: string_field(object, "method").unwrap_or_else(|| "POST".to_string()),
        method_name: string_field(object, "method_name").unwrap_or_default(),
        exchange: parse_exchange(string_field(object, "exchange").as_deref()),
        tx_scope: parse_tx_scope(string_field(object, "tx_scope").as_deref()),
        subevents: array_field(object, "subevents")
            .map(string_vec)
            .unwrap_or_default(),
        hooks: array_field(object, "hooks")
            .map(string_vec)
            .unwrap_or_default(),
        callback_fences: array_field(object, "callback_fences")
            .map(string_vec)
            .unwrap_or_default(),
        table: string_field(object, "table").unwrap_or_default(),
        engine_kind: string_field(object, "engine_kind").unwrap_or_else(|| "inmemory".to_string()),
        engine_language: string_field(object, "engine_language")
            .unwrap_or_else(|| "rust".to_string()),
        engine_callback: string_field(object, "engine_callback"),
        engine_options: object
            .get("engine_options")
            .map(value_from_json)
            .unwrap_or(Value::Null),
    })
}

fn decode_route(value: &JsonValue) -> RustResult<tigrbl_rs_kernel::plan::models::PlanRoute> {
    let object = value
        .as_object()
        .ok_or_else(|| "compiled route must be a JSOa object".to_string())?;
    Ok(tigrbl_rs_kernel::plan::models::PlanRoute {
        transport: string_field(object, "transport").unwrap_or_else(|| "rest".to_string()),
        family: string_field(object, "family").unwrap_or_else(|| "rest".to_string()),
        path: string_field(object, "path").unwrap_or_default(),
        method: string_field(object, "method").unwrap_or_else(|| "POST".to_string()),
        method_name: string_field(object, "method_name").unwrap_or_default(),
        binding_alias: string_field(object, "binding_alias").unwrap_or_default(),
        op_name: string_field(object, "op_name").unwrap_or_default(),
    })
}

fn value_to_json(value: &Value) -> JsonValue {
    match value {
        Value::Null => JsonValue::Null,
        Value::Bool(value) => JsonValue::Bool(*value),
        Value::Integer(value) => JsonValue::from(*value),
        Value::Float(value) => JsonValue::from(*value),
        Value::String(value) => JsonValue::String(value.clone()),
        Value::Bytes(value) => {
            JsonValue::Array(value.iter().map(|item| JsonValue::from(*item)).collect())
        }
        Value::Array(values) => JsonValue::Array(values.iter().map(value_to_json).collect()),
        Value::Object(values) => JsonValue::Object(
            values
                .iter()
                .map(|(key, value)| (key.clone(), value_to_json(value)))
                .collect(),
        ),
    }
}

fn value_from_json(value: &JsonValue) -> Value {
    match value {
        JsonValue::Null => Value::Null,
        JsonValue::Bool(value) => Value::Bool(*value),
        JsonValue::Number(value) => value
            .as_i64()
            .map(Value::Integer)
            .or_else(|| value.as_f64().map(Value::Float))
            .unwrap_or(Value::Null),
        JsonValue::String(value) => Value::String(value.clone()),
        JsonValue::Array(values) => Value::Array(values.iter().map(value_from_json).collect()),
        JsonValue::Object(values) => Value::Object(
            values
                .iter()
                .map(|(key, value)| (key.clone(), value_from_json(value)))
                .collect(),
        ),
    }
}

fn array_field<'a>(object: &'a Map<String, JsonValue>, name: &str) -> Option<&'a [JsonValue]> {
    object.get(name)?.as_array().map(Vec::as_slice)
}

fn string_field(object: &Map<String, JsonValue>, name: &str) -> Option<String> {
    match object.get(name)? {
        JsonValue::String(value) => Some(value.clone()),
        JsonValue::Number(value) => Some(value.to_string()),
        JsonValue::Bool(value) => Some(value.to_string()),
        _ => None,
    }
}

fn number_field(object: &Map<String, JsonValue>, name: &str) -> Option<usize> {
    object.get(name)?.as_u64().map(|value| value as usize)
}

fn string_vec(values: &[JsonValue]) -> Vec<String> {
    values
        .iter()
        .filter_map(|value| match value {
            JsonValue::String(value) => Some(value.clone()),
            _ => None,
        })
        .collect()
}

fn parse_op_kind(value: Option<&str>) -> OpKind {
    match value.unwrap_or("create") {
        "read" => OpKind::Read,
        "update" => OpKind::Update,
        "replace" => OpKind::Replace,
        "merge" => OpKind::Merge,
        "delete" => OpKind::Delete,
        "list" => OpKind::List,
        "clear" => OpKind::Clear,
        "count" => OpKind::Count,
        "exists" => OpKind::Exists,
        "bulk_create" => OpKind::BulkCreate,
        "bulk_update" => OpKind::BulkUpdate,
        "bulk_replace" => OpKind::BulkReplace,
        "bulk_merge" => OpKind::BulkMerge,
        "bulk_delete" => OpKind::BulkDelete,
        "aggregate" => OpKind::Aggregate,
        "group_by" => OpKind::GroupBy,
        "publish" => OpKind::Publish,
        "subscribe" => OpKind::Subscribe,
        "tail" => OpKind::Tail,
        "upload" => OpKind::Upload,
        "download" => OpKind::Download,
        "append_chunk" => OpKind::AppendChunk,
        "send_datagram" => OpKind::SendDatagram,
        "checkpoint" => OpKind::Checkpoint,
        "custom" => OpKind::Custom,
        _ => OpKind::Create,
    }
}

fn parse_exchange(value: Option<&str>) -> Exchange {
    match value.unwrap_or("request_response") {
        "server_stream" => Exchange::ServerStream,
        "client_stream" => Exchange::ClientStream,
        "bidirectional_stream" => Exchange::BidirectionalStream,
        _ => Exchange::RequestResponse,
    }
}

fn parse_tx_scope(value: Option<&str>) -> TxScope {
    match value.unwrap_or("inherit") {
        "none" => TxScope::None,
        "read_only" => TxScope::ReadOnly,
        "read_write" => TxScope::ReadWrite,
        _ => TxScope::Inherit,
    }
}
