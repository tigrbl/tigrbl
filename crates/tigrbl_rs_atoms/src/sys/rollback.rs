use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct RollbackAtom;

impl AtomStep for RollbackAtom {
    fn name(&self) -> &'static str {
        "sys.rollback"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
