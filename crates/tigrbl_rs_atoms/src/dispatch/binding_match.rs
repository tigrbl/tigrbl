use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct BindingMatchAtom;

impl AtomStep for BindingMatchAtom {
    fn name(&self) -> &'static str {
        "dispatch.binding_match"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Dispatch
    }
}
