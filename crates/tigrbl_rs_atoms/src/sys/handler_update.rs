use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerUpdateAtom;

impl AtomStep for HandlerUpdateAtom {
    fn name(&self) -> &'static str {
        "sys.handler_update"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
