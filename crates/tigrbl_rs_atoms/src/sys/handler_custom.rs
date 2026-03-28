use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerCustomAtom;

impl AtomStep for HandlerCustomAtom {
    fn name(&self) -> &'static str {
        "sys.handler_custom"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
