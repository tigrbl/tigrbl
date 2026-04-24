#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct StorageTypeRef {
    pub engine_kind: Option<String>,
    pub physical_name: String,
}

impl StorageTypeRef {
    pub fn new(physical_name: impl Into<String>, engine_kind: Option<impl Into<String>>) -> Self {
        Self {
            engine_kind: engine_kind.map(|value| value.into()),
            physical_name: physical_name.into(),
        }
    }
}
