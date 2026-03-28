use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct OutDumpAtom;

impl AtomStep for OutDumpAtom {
    fn name(&self) -> &'static str {
        "egress.out_dump"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Egress
    }
}
