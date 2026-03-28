#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct ReflectedDatatype {
    pub engine_kind: String,
    pub physical_name: String,
    pub logical_hint: Option<String>,
}
