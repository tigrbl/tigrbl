use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerCreateAtom;

impl AtomStep for HandlerCreateAtom {
    fn name(&self) -> &'static str {
        "sys.handler_create"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
