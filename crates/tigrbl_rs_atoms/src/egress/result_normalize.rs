use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct ResultNormalizeAtom;

impl AtomStep for ResultNormalizeAtom {
    fn name(&self) -> &'static str {
        "egress.result_normalize"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Egress
    }
}
