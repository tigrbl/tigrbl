use crate::{hook::HookSpec, op::OpSpec, table::TableSpec};

#[derive(Debug, Clone, Default, PartialEq)]
pub struct BindingSpec {
    pub alias: String,
    pub op: OpSpec,
    pub table: Option<TableSpec>,
    pub hooks: Vec<HookSpec>,
}
