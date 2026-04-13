use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerPublishAtom;

impl AtomStep for HandlerPublishAtom {
    fn name(&self) -> &'static str {
        "sys.handler_publish"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
