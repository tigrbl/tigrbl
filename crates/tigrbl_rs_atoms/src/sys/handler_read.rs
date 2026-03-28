use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerReadAtom;

impl AtomStep for HandlerReadAtom {
    fn name(&self) -> &'static str {
        "sys.handler_read"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
