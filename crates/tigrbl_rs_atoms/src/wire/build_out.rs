use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct BuildOutAtom;

impl AtomStep for BuildOutAtom {
    fn name(&self) -> &'static str {
        "wire.build_out"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Wire
    }
}
