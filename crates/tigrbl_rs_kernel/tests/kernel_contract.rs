use tigrbl_rs_kernel::KernelCompiler;
use tigrbl_rs_spec::{AppSpec, BindingSpec, OpKind, OpSpec};

#[test]
fn compiler_preserves_binding_aliases_and_packs_counts() {
    let mut app = AppSpec {
        name: "demo".to_string(),
        ..AppSpec::default()
    };
    app.bindings.push(BindingSpec {
        alias: "create_user".to_string(),
        op: OpSpec {
            kind: OpKind::Create,
            name: "create".to_string(),
            route: Some("/users".to_string()),
        },
        ..BindingSpec::default()
    });
    app.bindings.push(BindingSpec {
        alias: "bulk_create_users".to_string(),
        op: OpSpec {
            kind: OpKind::BulkCreate,
            name: "bulk_create".to_string(),
            route: Some("/users/bulk".to_string()),
        },
        ..BindingSpec::default()
    });

    let plan = KernelCompiler.compile(&app);
    assert_eq!(plan.app_name, "demo");
    assert_eq!(plan.bindings.len(), 2);
    assert_eq!(plan.bindings[0].alias, "create_user");
    let packed = plan.packed.expect("packed plan");
    assert_eq!(packed.segments, 2);
    assert_eq!(packed.fused_steps, 2);
    assert_eq!(packed.hot_paths, 1);
}
