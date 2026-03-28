use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerListAtom;

impl AtomStep for HandlerListAtom {
    fn name(&self) -> &'static str {
        "sys.handler_list"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
