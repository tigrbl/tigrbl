use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct PairedGenAtom;

impl AtomStep for PairedGenAtom {
    fn name(&self) -> &'static str {
        "resolve.paired_gen"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Resolve
    }
}
