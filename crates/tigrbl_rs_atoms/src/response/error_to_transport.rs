use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct ErrorToTransportAtom;

impl AtomStep for ErrorToTransportAtom {
    fn name(&self) -> &'static str {
        "response.error_to_transport"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Response
    }
}
