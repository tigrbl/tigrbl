use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct CtxInitAtom;

impl AtomStep for CtxInitAtom {
    fn name(&self) -> &'static str {
        "ingress.ctx_init"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Ingress
    }
}
