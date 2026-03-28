use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct DbAtom;

impl AtomStep for DbAtom {
    fn name(&self) -> &'static str {
        "sys.db"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
