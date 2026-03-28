use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerMergeAtom;

impl AtomStep for HandlerMergeAtom {
    fn name(&self) -> &'static str {
        "sys.handler_merge"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
