use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct ToTransportResponseAtom;

impl AtomStep for ToTransportResponseAtom {
    fn name(&self) -> &'static str {
        "egress.to_transport_response"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Egress
    }
}
