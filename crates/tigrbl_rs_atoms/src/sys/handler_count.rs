use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerCountAtom;

impl AtomStep for HandlerCountAtom {
    fn name(&self) -> &'static str {
        "sys.handler_count"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
