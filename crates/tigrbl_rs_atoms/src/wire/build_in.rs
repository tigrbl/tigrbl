use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct BuildInAtom;

impl AtomStep for BuildInAtom {
    fn name(&self) -> &'static str {
        "wire.build_in"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Wire
    }
}
