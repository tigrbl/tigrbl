use tigrbl_rs_spec::values::Value;

#[derive(Debug, Clone, Default, PartialEq)]
pub struct ListResult {
    pub rows: Vec<Value>,
    pub total: usize,
}
