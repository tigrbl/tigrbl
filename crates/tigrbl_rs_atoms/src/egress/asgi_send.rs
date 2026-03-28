use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct AsgiSendAtom;

impl AtomStep for AsgiSendAtom {
    fn name(&self) -> &'static str {
        "egress.asgi_send"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Egress
    }
}
