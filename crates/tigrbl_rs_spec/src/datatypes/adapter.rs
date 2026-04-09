use crate::datatypes::datatype_spec::DataTypeSpec;

pub trait DatatypeAdapter: Send + Sync {
    fn logical_name(&self) -> &str;
    fn normalize(&self, spec: &DataTypeSpec) -> DataTypeSpec;
    fn encode(&self, value: crate::values::Value) -> crate::values::Value {
        value
    }
    fn decode(&self, value: crate::values::Value) -> crate::values::Value {
        value
    }
}

#[derive(Debug, Clone)]
pub struct BaseDatatypeAdapter {
    logical_name: String,
}

impl BaseDatatypeAdapter {
    pub fn new(logical_name: impl Into<String>) -> Self {
        Self {
            logical_name: logical_name.into(),
        }
    }
}

impl DatatypeAdapter for BaseDatatypeAdapter {
    fn logical_name(&self) -> &str {
        &self.logical_name
    }

    fn normalize(&self, spec: &DataTypeSpec) -> DataTypeSpec {
        let mut normalized = spec.clone();
        normalized.logical_name = self.logical_name.clone();
        normalized
    }
}
