use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct AssembleAtom;

impl AtomStep for AssembleAtom {
    fn name(&self) -> &'static str {
        "resolve.assemble"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Resolve
    }
}
