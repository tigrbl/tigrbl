use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct SecurityAtom;

impl AtomStep for SecurityAtom {
    fn name(&self) -> &'static str {
        "dep.security"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Dep
    }
}
