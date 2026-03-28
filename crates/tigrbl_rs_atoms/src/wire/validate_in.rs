use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct ValidateInAtom;

impl AtomStep for ValidateInAtom {
    fn name(&self) -> &'static str {
        "wire.validate_in"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Wire
    }
}
