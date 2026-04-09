use std::collections::BTreeMap;

use crate::datatypes::storage_type_ref::StorageTypeRef;

#[derive(Debug, Clone, Default)]
pub struct EngineDatatypeRegistry {
    pub lowerers_by_engine: BTreeMap<String, BTreeMap<String, StorageTypeRef>>,
}

impl EngineDatatypeRegistry {
    pub fn register(
        &mut self,
        engine_kind: impl Into<String>,
        logical_name: impl Into<String>,
        storage_type: StorageTypeRef,
    ) {
        self.lowerers_by_engine
            .entry(engine_kind.into())
            .or_default()
            .insert(logical_name.into(), storage_type);
    }

    pub fn lower(
        &self,
        engine_kind: &str,
        logical_name: &str,
    ) -> Option<StorageTypeRef> {
        self.lowerers_by_engine
            .get(engine_kind)
            .and_then(|entries| entries.get(logical_name))
            .cloned()
    }
}
