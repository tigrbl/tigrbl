use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct BindingParseAtom;

impl AtomStep for BindingParseAtom {
    fn name(&self) -> &'static str {
        "dispatch.binding_parse"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Dispatch
    }
}
