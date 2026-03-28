use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerBulkReplaceAtom;

impl AtomStep for HandlerBulkReplaceAtom {
    fn name(&self) -> &'static str {
        "sys.handler_bulk_replace"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
