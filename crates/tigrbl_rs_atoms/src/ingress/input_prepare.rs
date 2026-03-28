use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct InputPrepareAtom;

impl AtomStep for InputPrepareAtom {
    fn name(&self) -> &'static str {
        "ingress.input_prepare"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Ingress
    }
}
