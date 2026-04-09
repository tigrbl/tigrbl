use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerCheckpointAtom;

impl AtomStep for HandlerCheckpointAtom {
    fn name(&self) -> &'static str {
        "sys.handler_checkpoint"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
