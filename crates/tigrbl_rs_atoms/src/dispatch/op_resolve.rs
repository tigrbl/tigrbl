use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct OpResolveAtom;

impl AtomStep for OpResolveAtom {
    fn name(&self) -> &'static str {
        "dispatch.op_resolve"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Dispatch
    }
}
