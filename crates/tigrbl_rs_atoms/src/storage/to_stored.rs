use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct ToStoredAtom;

impl AtomStep for ToStoredAtom {
    fn name(&self) -> &'static str {
        "storage.to_stored"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Storage
    }
}
