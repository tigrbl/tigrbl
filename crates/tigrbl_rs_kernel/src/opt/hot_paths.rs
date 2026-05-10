use crate::plan::models::KernelPlan;
use std::collections::BTreeMap;
use tigrbl_rs_spec::Value;

pub fn apply(mut plan: KernelPlan) -> KernelPlan {
    plan.routes.sort_by(|left, right| {
        left.transport
            .cmp(&right.transport)
            .then_with(|| left.family.cmp(&right.family))
            .then_with(|| left.path.cmp(&right.path))
            .then_with(|| left.method.cmp(&right.method))
            .then_with(|| left.binding_alias.cmp(&right.binding_alias))
    });
    let mut metadata = BTreeMap::new();
    metadata.insert(
        "layout".to_string(),
        Value::String("tiered-soa-hot-metadata".to_string()),
    );
    metadata.insert(
        "routes".to_string(),
        Value::Integer(plan.routes.len() as i64),
    );
    metadata.insert(
        "bindings".to_string(),
        Value::Integer(plan.bindings.len() as i64),
    );
    plan.metadata = Value::Object(metadata);
    plan
}
