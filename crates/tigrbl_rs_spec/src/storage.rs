use std::collections::BTreeMap;

use crate::{datatypes::storage_type_ref::StorageTypeRef, values::Value};

#[derive(Debug, Clone, Default, PartialEq)]
pub struct StorageSpec {
    pub physical_type: Option<StorageTypeRef>,
    pub indexed: bool,
    pub unique: bool,
    pub options: BTreeMap<String, Value>,
}
