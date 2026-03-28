use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerClearAtom;

impl AtomStep for HandlerClearAtom {
    fn name(&self) -> &'static str {
        "sys.handler_clear"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
