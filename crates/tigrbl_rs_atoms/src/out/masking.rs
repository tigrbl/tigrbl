use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct MaskingAtom;

impl AtomStep for MaskingAtom {
    fn name(&self) -> &'static str {
        "out.masking"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Out
    }
}
