use std::collections::BTreeMap;

use crate::datatypes::{
    adapter::{BaseDatatypeAdapter, DatatypeAdapter},
    datatype_spec::DataTypeSpec,
};

#[derive(Debug, Clone, Default)]
pub struct DatatypeRegistry {
    pub by_name: BTreeMap<String, DataTypeSpec>,
}

impl DatatypeRegistry {
    pub fn register(&mut self, datatype: DataTypeSpec) {
        self.by_name.insert(datatype.logical_name.clone(), datatype);
    }

    pub fn register_builtin(&mut self, logical_name: impl Into<String>) {
        let adapter = BaseDatatypeAdapter::new(logical_name.into());
        let spec = adapter.normalize(&DataTypeSpec::new(adapter.logical_name()));
        self.register(spec);
    }

    pub fn normalize(&self, spec: &DataTypeSpec) -> DataTypeSpec {
        self.by_name
            .get(&spec.logical_name)
            .cloned()
            .unwrap_or_else(|| spec.clone())
    }

    pub fn registered_names(&self) -> Vec<String> {
        self.by_name.keys().cloned().collect()
    }
}
