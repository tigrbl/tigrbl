use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct OltpContextAtom;

impl AtomStep for OltpContextAtom {
    fn name(&self) -> &'static str {
        "sys.oltp_context"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
