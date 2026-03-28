use crate::datatypes::{
    datatype_spec::DataTypeSpec, engine_registry::EngineDatatypeRegistry,
    storage_type_ref::StorageTypeRef,
};

#[derive(Debug, Clone, Default)]
pub struct EngineDatatypeBridge {
    pub registry: EngineDatatypeRegistry,
}

impl EngineDatatypeBridge {
    pub fn lower(&self, engine_kind: &str, datatype: &DataTypeSpec) -> StorageTypeRef {
        StorageTypeRef {
            engine_kind: Some(engine_kind.to_string()),
            physical_name: datatype.logical_name.clone(),
        }
    }
}
