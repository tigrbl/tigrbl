use crate::{datatypes::datatype_spec::DataTypeSpec, storage::StorageSpec};

#[derive(Debug, Clone, Default, PartialEq)]
pub struct ColumnSpec {
    pub name: String,
    pub datatype: DataTypeSpec,
    pub storage: Option<StorageSpec>,
    pub nullable: bool,
    pub primary_key: bool,
    pub default_expr: Option<String>,
}
