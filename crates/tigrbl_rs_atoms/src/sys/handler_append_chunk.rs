use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerAppendChunkAtom;

impl AtomStep for HandlerAppendChunkAtom {
    fn name(&self) -> &'static str {
        "sys.handler_append_chunk"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
