use crate::datatypes::{datatype_spec::DataTypeSpec, storage_type_ref::StorageTypeRef};

pub trait EngineTypeLowerer: Send + Sync {
    fn engine_kind(&self) -> &str;
    fn lower(&self, datatype: &DataTypeSpec) -> StorageTypeRef;
}
