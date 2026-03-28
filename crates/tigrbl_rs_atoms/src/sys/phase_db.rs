use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct PhaseDbAtom;

impl AtomStep for PhaseDbAtom {
    fn name(&self) -> &'static str {
        "sys.phase_db"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
