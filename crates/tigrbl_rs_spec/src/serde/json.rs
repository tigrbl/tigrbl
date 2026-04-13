use std::collections::BTreeMap;

use serde_json::{Map, Value as JsonValue};

use crate::{
    app::AppSpec,
    binding::BindingSpec,
    engine::EngineSpec,
    errors::SpecError,
    hook::{HookPhase, HookSpec},
    op::{Exchange, OpKind, OpSpec, TxScope},
    request::RequestEnvelope,
    response::ResponseEnvelope,
    table::TableSpec,
    values::Value,
};

pub fn to_json(value: &AppSpec) -> Result<String, SpecError> {
    serde_json::to_string_pretty(&app_to_json(value))
        .map_err(|err| SpecError::Serialization(err.to_string()))
}

pub fn from_json(raw: &str) -> Result<AppSpec, SpecError> {
    let parsed: JsonValue =
        serde_json::from_str(raw).map_err(|err| SpecError::Invalid(err.to_string()))?;
    let object = parsed
        .as_object()
        .ok_or_else(|| SpecError::Invalid("spec payload must be a JSON object".to_string()))?;

    let mut spec = AppSpec::default();
    spec.name = string_field(object, "name").unwrap_or_default();
    spec.title = string_field(object, "title").unwrap_or_else(|| spec.name.clone());
    spec.version = string_field(object, "version").unwrap_or_else(|| spec.version.clone());
    spec.jsonrpc_prefix =
        string_field(object, "jsonrpc_prefix").unwrap_or_else(|| spec.jsonrpc_prefix.clone());
    spec.system_prefix =
        string_field(object, "system_prefix").unwrap_or_else(|| spec.system_prefix.clone());
    spec.metadata = object_field(object, "metadata")
        .map(string_map)
        .unwrap_or_default();
    spec.bindings = array_field(object, "bindings")
        .map(parse_bindings)
        .transpose()?
        .unwrap_or_default();
    spec.tables = array_field(object, "tables")
        .map(parse_tables)
        .transpose()?
        .unwrap_or_default();
    spec.engines = array_field(object, "engines")
        .map(parse_engines)
        .transpose()?
        .unwrap_or_default();

    if spec.name.trim().is_empty() {
        return Err(SpecError::Invalid("spec.name must be present".to_string()));
    }

    Ok(spec)
}

pub fn request_to_json(value: &RequestEnvelope) -> JsonValue {
    let mut object = Map::new();
    object.insert("operation".to_string(), JsonValue::String(value.operation.clone()));
    object.insert("transport".to_string(), JsonValue::String(value.transport.clone()));
    object.insert("path".to_string(), JsonValue::String(value.path.clone()));
    object.insert("method".to_string(), JsonValue::String(value.method.clone()));
    object.insert(
        "path_params".to_string(),
        JsonValue::Object(value_map_to_json(&value.path_params)),
    );
    object.insert(
        "query_params".to_string(),
        JsonValue::Object(value_map_to_json(&value.query_params)),
    );
    object.insert(
        "headers".to_string(),
        JsonValue::Object(
            value
                .headers
                .iter()
                .map(|(key, value)| (key.clone(), JsonValue::String(value.clone())))
                .collect(),
        ),
    );
    object.insert("body".to_string(), value_to_json(&value.body));
    JsonValue::Object(object)
}

pub fn request_from_json(raw: &str) -> Result<RequestEnvelope, SpecError> {
    let parsed: JsonValue =
        serde_json::from_str(raw).map_err(|err| SpecError::Invalid(err.to_string()))?;
    let object = parsed.as_object().ok_or_else(|| {
        SpecError::Invalid("request payload must be a JSON object".to_string())
    })?;

    Ok(RequestEnvelope {
        operation: string_field(object, "operation").unwrap_or_default(),
        transport: string_field(object, "transport").unwrap_or_else(|| "rest".to_string()),
        path: string_field(object, "path").unwrap_or_default(),
        method: string_field(object, "method").unwrap_or_default(),
        path_params: object_field(object, "path_params")
            .map(value_map_from_json)
            .unwrap_or_default(),
        query_params: object_field(object, "query_params")
            .map(value_map_from_json)
            .unwrap_or_default(),
        headers: object_field(object, "headers")
            .map(string_map)
            .unwrap_or_default(),
        body: object
            .get("body")
            .map(value_from_json)
            .unwrap_or(Value::Null),
    })
}

pub fn response_to_json(value: &ResponseEnvelope) -> Result<String, SpecError> {
    serde_json::to_string_pretty(&JsonValue::Object(response_to_json_object(value)))
        .map_err(|err| SpecError::Serialization(err.to_string()))
}

fn parse_bindings(values: &[JsonValue]) -> Result<Vec<BindingSpec>, SpecError> {
    values.iter().map(parse_binding).collect()
}

fn parse_binding(value: &JsonValue) -> Result<BindingSpec, SpecError> {
    let object = value
        .as_object()
        .ok_or_else(|| SpecError::Invalid("binding must be a JSON object".to_string()))?;

    Ok(BindingSpec {
        alias: string_field(object, "alias").unwrap_or_default(),
        transport: string_field(object, "transport").unwrap_or_else(|| "rest".to_string()),
        path: string_field(object, "path")
            .or_else(|| string_field(object, "route"))
            .map(Some)
            .unwrap_or(None),
        family: string_field(object, "family")
            .or_else(|| string_field(object, "transport"))
            .unwrap_or_else(|| "rest".to_string()),
        framing: string_field(object, "framing").map(Some).unwrap_or(None),
        op: parse_op(object.get("op").unwrap_or(&JsonValue::Null))?,
        table: object.get("table").map(parse_table).transpose()?,
        hooks: array_field(object, "hooks")
            .map(parse_hooks)
            .transpose()?
            .unwrap_or_default(),
    })
}

fn parse_hooks(values: &[JsonValue]) -> Result<Vec<HookSpec>, SpecError> {
    values.iter().map(parse_hook).collect()
}

fn parse_hook(value: &JsonValue) -> Result<HookSpec, SpecError> {
    let object = value
        .as_object()
        .ok_or_else(|| SpecError::Invalid("hook must be a JSON object".to_string()))?;

    Ok(HookSpec {
        name: string_field(object, "name").unwrap_or_default(),
        phase: string_to_hook_phase(string_field(object, "phase").as_deref()),
        bindings: array_field(object, "bindings")
            .map(string_vec)
            .unwrap_or_default(),
        exchange: string_field(object, "exchange")
            .map(|value| string_to_exchange(Some(value.as_str()))),
        family: array_field(object, "family")
            .map(string_vec)
            .unwrap_or_default(),
        subevents: array_field(object, "subevents")
            .map(string_vec)
            .unwrap_or_default(),
        metadata: object
            .get("metadata")
            .map(value_from_json)
            .unwrap_or(Value::Null),
    })
}

fn parse_op(value: &JsonValue) -> Result<OpSpec, SpecError> {
    let object = value
        .as_object()
        .ok_or_else(|| SpecError::Invalid("binding.op must be a JSON object".to_string()))?;

    Ok(OpSpec {
        kind: string_to_op_kind(
            string_field(object, "kind")
                .or_else(|| string_field(object, "name"))
                .as_deref(),
        ),
        name: string_field(object, "name").unwrap_or_default(),
        route: string_field(object, "route")
            .or_else(|| string_field(object, "path"))
            .map(Some)
            .unwrap_or(None),
        exchange: string_to_exchange(string_field(object, "exchange").as_deref()),
        tx_scope: string_to_tx_scope(string_field(object, "tx_scope").as_deref()),
        subevents: array_field(object, "subevents")
            .map(string_vec)
            .unwrap_or_default(),
    })
}

fn parse_tables(values: &[JsonValue]) -> Result<Vec<TableSpec>, SpecError> {
    values.iter().map(parse_table).collect()
}

fn parse_table(value: &JsonValue) -> Result<TableSpec, SpecError> {
    let object = value
        .as_object()
        .ok_or_else(|| SpecError::Invalid("table must be a JSON object".to_string()))?;
    Ok(TableSpec {
        name: string_field(object, "name").unwrap_or_default(),
        columns: Vec::new(),
    })
}

fn parse_engines(values: &[JsonValue]) -> Result<Vec<EngineSpec>, SpecError> {
    values.iter().map(parse_engine).collect()
}

fn parse_engine(value: &JsonValue) -> Result<EngineSpec, SpecError> {
    let object = value
        .as_object()
        .ok_or_else(|| SpecError::Invalid("engine must be a JSON object".to_string()))?;
    Ok(EngineSpec {
        name: string_field(object, "name").unwrap_or_default(),
        kind: string_field(object, "kind").unwrap_or_else(|| "inmemory".to_string()),
        options: object_field(object, "options")
            .map(value_map_from_json)
            .unwrap_or_default(),
    })
}

fn app_to_json(value: &AppSpec) -> JsonValue {
    let mut object = Map::new();
    object.insert("name".to_string(), JsonValue::String(value.name.clone()));
    object.insert("title".to_string(), JsonValue::String(value.title.clone()));
    object.insert("version".to_string(), JsonValue::String(value.version.clone()));
    object.insert(
        "jsonrpc_prefix".to_string(),
        JsonValue::String(value.jsonrpc_prefix.clone()),
    );
    object.insert(
        "system_prefix".to_string(),
        JsonValue::String(value.system_prefix.clone()),
    );
    object.insert(
        "metadata".to_string(),
        JsonValue::Object(
            value
                .metadata
                .iter()
                .map(|(key, value)| (key.clone(), JsonValue::String(value.clone())))
                .collect(),
        ),
    );
    object.insert(
        "bindings".to_string(),
        JsonValue::Array(value.bindings.iter().map(binding_to_json).collect()),
    );
    object.insert(
        "tables".to_string(),
        JsonValue::Array(
            value
                .tables
                .iter()
                .map(|table| {
                    let mut table_object = Map::new();
                    table_object.insert("name".to_string(), JsonValue::String(table.name.clone()));
                    table_object.insert("columns".to_string(), JsonValue::Array(Vec::new()));
                    JsonValue::Object(table_object)
                })
                .collect(),
        ),
    );
    object.insert(
        "engines".to_string(),
        JsonValue::Array(
            value
                .engines
                .iter()
                .map(|engine| {
                    let mut engine_object = Map::new();
                    engine_object.insert("name".to_string(), JsonValue::String(engine.name.clone()));
                    engine_object.insert("kind".to_string(), JsonValue::String(engine.kind.clone()));
                    engine_object.insert(
                        "options".to_string(),
                        JsonValue::Object(value_map_to_json(&engine.options)),
                    );
                    JsonValue::Object(engine_object)
                })
                .collect(),
        ),
    );
    JsonValue::Object(object)
}

fn binding_to_json(value: &BindingSpec) -> JsonValue {
    let mut object = Map::new();
    object.insert("alias".to_string(), JsonValue::String(value.alias.clone()));
    object.insert("transport".to_string(), JsonValue::String(value.transport.clone()));
    object.insert("family".to_string(), JsonValue::String(value.family.clone()));
    if let Some(path) = &value.path {
        object.insert("path".to_string(), JsonValue::String(path.clone()));
    }
    if let Some(framing) = &value.framing {
        object.insert("framing".to_string(), JsonValue::String(framing.clone()));
    }
    object.insert("op".to_string(), op_to_json(&value.op));
    if let Some(table) = &value.table {
        object.insert(
            "table".to_string(),
            JsonValue::Object(
                [("name".to_string(), JsonValue::String(table.name.clone()))]
                    .into_iter()
                    .collect(),
            ),
        );
    }
    object.insert(
        "hooks".to_string(),
        JsonValue::Array(
            value
                .hooks
                .iter()
                .map(|hook| {
                    let mut hook_object = Map::new();
                    hook_object.insert("name".to_string(), JsonValue::String(hook.name.clone()));
                    hook_object.insert(
                        "phase".to_string(),
                        JsonValue::String(hook.phase.as_str().to_string()),
                    );
                    JsonValue::Object(hook_object)
                })
                .collect(),
        ),
    );
    JsonValue::Object(object)
}

fn op_to_json(value: &OpSpec) -> JsonValue {
    let mut object = Map::new();
    object.insert("kind".to_string(), JsonValue::String(value.kind.as_str().to_string()));
    object.insert("name".to_string(), JsonValue::String(value.name.clone()));
    if let Some(route) = &value.route {
        object.insert("route".to_string(), JsonValue::String(route.clone()));
    }
    object.insert(
        "exchange".to_string(),
        JsonValue::String(value.exchange.as_str().to_string()),
    );
    object.insert(
        "tx_scope".to_string(),
        JsonValue::String(value.tx_scope.as_str().to_string()),
    );
    object.insert(
        "subevents".to_string(),
        JsonValue::Array(
            value
                .subevents
                .iter()
                .cloned()
                .map(JsonValue::String)
                .collect(),
        ),
    );
    JsonValue::Object(object)
}

fn response_to_json_object(value: &ResponseEnvelope) -> Map<String, JsonValue> {
    let mut object = Map::new();
    object.insert("status".to_string(), JsonValue::from(value.status));
    object.insert(
        "headers".to_string(),
        JsonValue::Object(
            value
                .headers
                .iter()
                .map(|(key, value)| (key.clone(), JsonValue::String(value.clone())))
                .collect(),
        ),
    );
    object.insert("body".to_string(), value_to_json(&value.body));
    object
}

fn value_map_to_json(values: &BTreeMap<String, Value>) -> Map<String, JsonValue> {
    values
        .iter()
        .map(|(key, value)| (key.clone(), value_to_json(value)))
        .collect()
}

fn value_map_from_json(values: &Map<String, JsonValue>) -> BTreeMap<String, Value> {
    values
        .iter()
        .map(|(key, value)| (key.clone(), value_from_json(value)))
        .collect()
}

fn value_to_json(value: &Value) -> JsonValue {
    match value {
        Value::Null => JsonValue::Null,
        Value::Bool(value) => JsonValue::Bool(*value),
        Value::Integer(value) => JsonValue::from(*value),
        Value::Float(value) => JsonValue::from(*value),
        Value::String(value) => JsonValue::String(value.clone()),
        Value::Bytes(value) => JsonValue::Array(
            value
                .iter()
                .map(|item| JsonValue::from(*item))
                .collect(),
        ),
        Value::Array(values) => JsonValue::Array(values.iter().map(value_to_json).collect()),
        Value::Object(values) => JsonValue::Object(value_map_to_json(values)),
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
        JsonValue::Object(values) => Value::Object(value_map_from_json(values)),
    }
}

fn object_field<'a>(
    object: &'a Map<String, JsonValue>,
    name: &str,
) -> Option<&'a Map<String, JsonValue>> {
    object.get(name)?.as_object()
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

fn string_map(object: &Map<String, JsonValue>) -> BTreeMap<String, String> {
    object
        .iter()
        .filter_map(|(key, value)| match value {
            JsonValue::String(value) => Some((key.clone(), value.clone())),
            JsonValue::Number(value) => Some((key.clone(), value.to_string())),
            JsonValue::Bool(value) => Some((key.clone(), value.to_string())),
            _ => None,
        })
        .collect()
}

fn string_vec(values: &[JsonValue]) -> Vec<String> {
    values
        .iter()
        .filter_map(|value| match value {
            JsonValue::String(value) => Some(value.clone()),
            JsonValue::Number(value) => Some(value.to_string()),
            JsonValue::Bool(value) => Some(value.to_string()),
            _ => None,
        })
        .collect()
}

fn string_to_op_kind(value: Option<&str>) -> OpKind {
    match value.unwrap_or("create") {
        "create" => OpKind::Create,
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
        _ => OpKind::Custom,
    }
}

fn string_to_exchange(value: Option<&str>) -> Exchange {
    match value.unwrap_or("request_response") {
        "server_stream" => Exchange::ServerStream,
        "client_stream" => Exchange::ClientStream,
        "bidirectional_stream" => Exchange::BidirectionalStream,
        _ => Exchange::RequestResponse,
    }
}

fn string_to_tx_scope(value: Option<&str>) -> TxScope {
    match value.unwrap_or("inherit") {
        "none" => TxScope::None,
        "read_only" => TxScope::ReadOnly,
        "read_write" => TxScope::ReadWrite,
        _ => TxScope::Inherit,
    }
}

fn string_to_hook_phase(value: Option<&str>) -> HookPhase {
    match value.unwrap_or("pre_tx_begin") {
        "start_tx" => HookPhase::StartTx,
        "pre_handler" => HookPhase::PreHandler,
        "handler" => HookPhase::Handler,
        "post_handler" => HookPhase::PostHandler,
        "pre_commit" => HookPhase::PreCommit,
        "end_tx" => HookPhase::EndTx,
        "post_commit" => HookPhase::PostCommit,
        "post_response" => HookPhase::PostResponse,
        "on_error" => HookPhase::OnError,
        "rollback" => HookPhase::Rollback,
        "custom" => HookPhase::Custom,
        _ => HookPhase::PreTxBegin,
    }
}
