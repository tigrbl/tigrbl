use tigrbl_rs_spec::{
    AppSpec, DataTypeSpec, DatatypeRegistry, EngineDatatypeBridge, EngineDatatypeRegistry,
    Exchange, HookPhase, OpKind, ReflectedTypeMapper, StorageTypeRef, TxScope,
};

#[test]
fn appspec_defaults_match_python_surface_prefixes() {
    let spec = AppSpec::default();
    assert_eq!(spec.version, "0.1.0");
    assert_eq!(spec.jsonrpc_prefix, "/rpc");
    assert_eq!(spec.system_prefix, "/system");
}

#[test]
fn opkind_exposes_bulk_variants() {
    assert!(OpKind::BulkCreate.is_bulk());
    assert_eq!(OpKind::BulkDelete.as_str(), "bulk_delete");
    assert_eq!(OpKind::Merge.as_str(), "merge");
    assert_eq!(OpKind::Count.as_str(), "count");
    assert_eq!(OpKind::Exists.as_str(), "exists");
    assert_eq!(OpKind::Aggregate.as_str(), "aggregate");
    assert_eq!(OpKind::GroupBy.as_str(), "group_by");
    assert_eq!(OpKind::Publish.as_str(), "publish");
    assert_eq!(OpKind::Checkpoint.as_str(), "checkpoint");
}

#[test]
fn hook_phases_cover_transaction_and_response_lifecycle() {
    assert_eq!(HookPhase::PreTxBegin.as_str(), "pre_tx_begin");
    assert_eq!(HookPhase::PostResponse.as_str(), "post_response");
    assert_eq!(HookPhase::Rollback.as_str(), "rollback");
}

#[test]
fn exchange_and_tx_scope_match_python_surface_literals() {
    assert_eq!(Exchange::RequestResponse.as_str(), "request_response");
    assert_eq!(Exchange::ServerStream.as_str(), "server_stream");
    assert_eq!(Exchange::BidirectionalStream.as_str(), "bidirectional_stream");
    assert_eq!(TxScope::Inherit.as_str(), "inherit");
    assert_eq!(TxScope::ReadOnly.as_str(), "read_only");
    assert_eq!(TxScope::ReadWrite.as_str(), "read_write");
}

#[test]
fn engine_bridge_uses_registered_lowering_before_fallback() {
    let mut registry = EngineDatatypeRegistry::default();
    registry.register(
        "sqlite",
        "string",
        StorageTypeRef::new("TEXT", Some("sqlite")),
    );

    let bridge = EngineDatatypeBridge { registry };
    let lowered = bridge.lower("sqlite", &DataTypeSpec::new("string"));
    assert_eq!(lowered.physical_name, "TEXT");

    let fallback = bridge.lower("sqlite", &DataTypeSpec::new("integer"));
    assert_eq!(fallback.physical_name, "integer");
}

#[test]
fn datatype_registry_normalizes_registered_specs() {
    let mut registry = DatatypeRegistry::default();
    registry.register(DataTypeSpec::new("string"));
    let normalized = registry.normalize(&DataTypeSpec::new("string"));
    assert_eq!(normalized.logical_name, "string");
    assert_eq!(registry.registered_names(), vec!["string".to_string()]);
}

#[test]
fn builtin_engine_registry_and_reflection_mapper_cover_next_target_surface() {
    let bridge = EngineDatatypeBridge::with_builtins();
    let lowered = bridge.lower("postgres", &DataTypeSpec::new("json"));
    assert_eq!(lowered.physical_name, "JSONB");

    let reflected = ReflectedTypeMapper::from_storage_ref(
        &StorageTypeRef::new("JSONB", Some("postgres")),
        "metadata_preserving",
        false,
    )
    .expect("reflection should succeed");
    assert_eq!(reflected.logical_name, "json");
    assert!(reflected.options.contains_key("reflected_engine_kind"));
}

#[test]
fn canonical_json_roundtrip_restores_rust_spec() {
    let raw = r#"{
        "name": "demo",
        "title": "Demo",
        "bindings": [
            {
                "alias": "users.create",
                "transport": "rest",
                "path": "/users",
                "op": {
                    "name": "create",
                    "kind": "create",
                    "route": "/users",
                    "exchange": "request_response",
                    "tx_scope": "read_write"
                },
                "table": {"name": "users"}
            }
        ],
        "engines": [{"name": "default", "kind": "inmemory"}]
    }"#;

    let parsed = tigrbl_rs_spec::serde::json::from_json(raw).unwrap();
    assert_eq!(parsed.name, "demo");
    assert_eq!(parsed.bindings[0].alias, "users.create");
    assert_eq!(parsed.bindings[0].op.kind, OpKind::Create);

    let reencoded = tigrbl_rs_spec::serde::json::to_json(&parsed).unwrap();
    let restored = tigrbl_rs_spec::serde::json::from_json(&reencoded).unwrap();
    assert_eq!(restored.name, "demo");
    assert_eq!(restored.engines[0].kind, "inmemory");
}
