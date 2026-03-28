use std::collections::BTreeMap;

use crate::phases::AtomPhase;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AtomMetadata {
    pub name: String,
    pub phase: AtomPhase,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AtomRegistryError {
    pub name: String,
}

#[derive(Debug, Clone, Default)]
pub struct AtomRegistry {
    pub atoms: BTreeMap<String, AtomMetadata>,
}

impl AtomRegistry {
    pub fn register(&mut self, metadata: AtomMetadata) {
        self.atoms.insert(metadata.name.clone(), metadata);
    }

    pub fn try_register(&mut self, metadata: AtomMetadata) -> Result<(), AtomRegistryError> {
        if self.atoms.contains_key(&metadata.name) {
            return Err(AtomRegistryError {
                name: metadata.name,
            });
        }
        self.atoms.insert(metadata.name.clone(), metadata);
        Ok(())
    }

    pub fn contains(&self, name: &str) -> bool {
        self.atoms.contains_key(name)
    }

    pub fn len(&self) -> usize {
        self.atoms.len()
    }
}
