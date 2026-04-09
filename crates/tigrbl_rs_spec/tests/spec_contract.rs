use tigrbl_rs_spec::{AppSpec, HookPhase, OpKind};

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
