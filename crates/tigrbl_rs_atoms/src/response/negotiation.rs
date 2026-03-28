use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct NegotiationAtom;

impl AtomStep for NegotiationAtom {
    fn name(&self) -> &'static str {
        "response.negotiation"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Response
    }
}
