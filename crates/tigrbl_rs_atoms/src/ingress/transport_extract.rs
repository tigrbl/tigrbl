use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct TransportExtractAtom;

impl AtomStep for TransportExtractAtom {
    fn name(&self) -> &'static str {
        "ingress.transport_extract"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Ingress
    }
}
