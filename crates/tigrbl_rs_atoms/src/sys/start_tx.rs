use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct StartTxAtom;

impl AtomStep for StartTxAtom {
    fn name(&self) -> &'static str {
        "sys.start_tx"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
