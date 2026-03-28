use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerBulkDeleteAtom;

impl AtomStep for HandlerBulkDeleteAtom {
    fn name(&self) -> &'static str {
        "sys.handler_bulk_delete"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
