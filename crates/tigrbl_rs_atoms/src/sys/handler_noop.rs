use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerNoopAtom;

impl AtomStep for HandlerNoopAtom {
    fn name(&self) -> &'static str {
        "sys.handler_noop"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
