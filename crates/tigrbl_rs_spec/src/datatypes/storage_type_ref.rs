#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct StorageTypeRef {
    pub engine_kind: Option<String>,
    pub physical_name: String,
}
