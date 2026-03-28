use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HeadersApplyAtom;

impl AtomStep for HeadersApplyAtom {
    fn name(&self) -> &'static str {
        "egress.headers_apply"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Egress
    }
}
