use crate::ColumnSpec;

#[derive(Debug, Clone, Default, PartialEq)]
pub struct TableSpec {
    pub name: String,
    pub columns: Vec<ColumnSpec>,
}
