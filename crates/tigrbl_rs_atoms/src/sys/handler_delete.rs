use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerDeleteAtom;

impl AtomStep for HandlerDeleteAtom {
    fn name(&self) -> &'static str {
        "sys.handler_delete"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
