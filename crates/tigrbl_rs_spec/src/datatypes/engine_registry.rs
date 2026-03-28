use std::collections::BTreeMap;

#[derive(Debug, Clone, Default)]
pub struct EngineDatatypeRegistry {
    pub lowerers_by_engine: BTreeMap<String, Vec<String>>,
}
