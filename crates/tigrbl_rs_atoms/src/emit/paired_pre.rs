use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct PairedPreAtom;

impl AtomStep for PairedPreAtom {
    fn name(&self) -> &'static str {
        "emit.paired_pre"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Emit
    }
}
