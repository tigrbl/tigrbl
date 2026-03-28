use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HeadersFromPayloadAtom;

impl AtomStep for HeadersFromPayloadAtom {
    fn name(&self) -> &'static str {
        "response.headers_from_payload"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Response
    }
}
