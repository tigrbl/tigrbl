use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HttpFinalizeAtom;

impl AtomStep for HttpFinalizeAtom {
    fn name(&self) -> &'static str {
        "egress.http_finalize"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Egress
    }
}
