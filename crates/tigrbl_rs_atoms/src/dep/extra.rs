use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct ExtraAtom;

impl AtomStep for ExtraAtom {
    fn name(&self) -> &'static str {
        "dep.extra"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Dep
    }
}
