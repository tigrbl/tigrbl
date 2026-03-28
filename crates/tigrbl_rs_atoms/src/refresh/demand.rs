use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct DemandAtom;

impl AtomStep for DemandAtom {
    fn name(&self) -> &'static str {
        "refresh.demand"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Refresh
    }
}
