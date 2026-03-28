use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerBulkCreateAtom;

impl AtomStep for HandlerBulkCreateAtom {
    fn name(&self) -> &'static str {
        "sys.handler_bulk_create"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
