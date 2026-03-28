use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct InputNormalizeAtom;

impl AtomStep for InputNormalizeAtom {
    fn name(&self) -> &'static str {
        "dispatch.input_normalize"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Dispatch
    }
}
