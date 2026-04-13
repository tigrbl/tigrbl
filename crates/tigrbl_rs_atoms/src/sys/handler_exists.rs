use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerExistsAtom;

impl AtomStep for HandlerExistsAtom {
    fn name(&self) -> &'static str {
        "sys.handler_exists"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
