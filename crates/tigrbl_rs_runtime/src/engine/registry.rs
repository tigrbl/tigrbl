use std::collections::BTreeMap;

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct EngineRegistry {
    pub engines: BTreeMap<String, String>,
}
