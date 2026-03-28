use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerBulkMergeAtom;

impl AtomStep for HandlerBulkMergeAtom {
    fn name(&self) -> &'static str {
        "sys.handler_bulk_merge"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
