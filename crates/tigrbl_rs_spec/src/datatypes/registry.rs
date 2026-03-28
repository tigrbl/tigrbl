use std::collections::BTreeMap;

use crate::datatypes::datatype_spec::DataTypeSpec;

#[derive(Debug, Clone, Default)]
pub struct DatatypeRegistry {
    pub by_name: BTreeMap<String, DataTypeSpec>,
}

impl DatatypeRegistry {
    pub fn register(&mut self, datatype: DataTypeSpec) {
        self.by_name.insert(datatype.logical_name.clone(), datatype);
    }
}
