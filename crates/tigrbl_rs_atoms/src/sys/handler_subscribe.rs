use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerSubscribeAtom;

impl AtomStep for HandlerSubscribeAtom {
    fn name(&self) -> &'static str {
        "sys.handler_subscribe"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
