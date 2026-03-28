use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct DumpAtom;

impl AtomStep for DumpAtom {
    fn name(&self) -> &'static str {
        "wire.dump"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Wire
    }
}
