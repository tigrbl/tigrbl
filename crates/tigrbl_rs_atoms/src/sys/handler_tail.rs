use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerTailAtom;

impl AtomStep for HandlerTailAtom {
    fn name(&self) -> &'static str {
        "sys.handler_tail"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
