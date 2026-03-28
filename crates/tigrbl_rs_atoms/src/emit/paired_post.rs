use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct PairedPostAtom;

impl AtomStep for PairedPostAtom {
    fn name(&self) -> &'static str {
        "emit.paired_post"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Emit
    }
}
