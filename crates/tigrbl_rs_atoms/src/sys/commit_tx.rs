use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct CommitTxAtom;

impl AtomStep for CommitTxAtom {
    fn name(&self) -> &'static str {
        "sys.commit_tx"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
