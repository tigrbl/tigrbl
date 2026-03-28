use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct EnvelopeApplyAtom;

impl AtomStep for EnvelopeApplyAtom {
    fn name(&self) -> &'static str {
        "egress.envelope_apply"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Egress
    }
}
