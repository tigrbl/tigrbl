use tigrbl_rs_spec::values::Value;

#[derive(Debug, Clone, Default, PartialEq)]
pub struct MutationResult {
    pub body: Value,
    pub affected_rows: usize,
}
