use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerBulkUpdateAtom;

impl AtomStep for HandlerBulkUpdateAtom {
    fn name(&self) -> &'static str {
        "sys.handler_bulk_update"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
