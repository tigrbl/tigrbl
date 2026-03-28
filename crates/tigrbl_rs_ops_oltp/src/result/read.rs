use tigrbl_rs_spec::values::Value;

#[derive(Debug, Clone, Default, PartialEq)]
pub struct ReadResult {
    pub body: Value,
}
