use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct NegotiateAtom;

impl AtomStep for NegotiateAtom {
    fn name(&self) -> &'static str {
        "response.negotiate"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Response
    }
}
