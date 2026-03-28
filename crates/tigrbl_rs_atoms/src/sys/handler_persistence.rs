use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerPersistenceAtom;

impl AtomStep for HandlerPersistenceAtom {
    fn name(&self) -> &'static str {
        "sys.handler_persistence"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
