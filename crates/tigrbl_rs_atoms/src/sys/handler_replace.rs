use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerReplaceAtom;

impl AtomStep for HandlerReplaceAtom {
    fn name(&self) -> &'static str {
        "sys.handler_replace"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
