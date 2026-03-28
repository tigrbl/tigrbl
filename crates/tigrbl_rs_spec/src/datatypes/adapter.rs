use crate::datatypes::datatype_spec::DataTypeSpec;

pub trait DatatypeAdapter: Send + Sync {
    fn logical_name(&self) -> &str;
    fn normalize(&self, spec: &DataTypeSpec) -> DataTypeSpec;
}
