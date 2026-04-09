use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerGroupByAtom;

impl AtomStep for HandlerGroupByAtom {
    fn name(&self) -> &'static str {
        "sys.handler_group_by"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
