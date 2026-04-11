use tigrbl_rs_ops_oltp::{
    bulk::{
        create::BulkCreateVerb, delete::BulkDeleteVerb, merge::BulkMergeVerb,
        replace::BulkReplaceVerb, update::BulkUpdateVerb, NativeBulkVerb,
    },
    handlers::{custom::CustomHandlerDescriptor, registry::HandlerRegistry},
    model,
    verbs::{
        clear::ClearVerb, create::CreateVerb, delete::DeleteVerb, list::ListVerb, merge::MergeVerb,
        read::ReadVerb, replace::ReplaceVerb, update::UpdateVerb, NativeOltpVerb,
    },
};
use tigrbl_rs_spec::OpKind;

#[test]
fn oltp_verbs_report_expected_name_and_kind() {
    let verbs: [(&str, OpKind, &dyn NativeOltpVerb); 8] = [
        ("create", OpKind::Create, &CreateVerb),
        ("read", OpKind::Read, &ReadVerb),
        ("update", OpKind::Update, &UpdateVerb),
        ("replace", OpKind::Replace, &ReplaceVerb),
        ("merge", OpKind::Merge, &MergeVerb),
        ("delete", OpKind::Delete, &DeleteVerb),
        ("list", OpKind::List, &ListVerb),
        ("clear", OpKind::Clear, &ClearVerb),
    ];

    for (name, kind, verb) in verbs {
        assert_eq!(verb.name(), name);
        assert_eq!(verb.kind(), kind);
    }
}

#[test]
fn bulk_verbs_report_expected_names() {
    let verbs: [(&str, &dyn NativeBulkVerb); 5] = [
        ("bulk_create", &BulkCreateVerb),
        ("bulk_update", &BulkUpdateVerb),
        ("bulk_replace", &BulkReplaceVerb),
        ("bulk_merge", &BulkMergeVerb),
        ("bulk_delete", &BulkDeleteVerb),
    ];

    for (name, verb) in verbs {
        assert_eq!(verb.name(), name);
    }
}

#[test]
fn handler_structs_and_model_modules_have_stable_defaults() {
    let registry = HandlerRegistry::default();
    assert!(registry.handlers.is_empty());

    let descriptor = CustomHandlerDescriptor::default();
    assert!(descriptor.name.is_empty());

    assert_eq!(model::defaults::MODULE, "model.defaults");
    assert_eq!(model::enums::MODULE, "model.enums");
    assert_eq!(model::filters::MODULE, "model.filters");
    assert_eq!(model::materialize::MODULE, "model.materialize");
    assert_eq!(model::normalize::MODULE, "model.normalize");
    assert_eq!(model::patch::MODULE, "model.patch");
}
