use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct RendererAtom;

impl AtomStep for RendererAtom {
    fn name(&self) -> &'static str {
        "response.renderer"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Response
    }
}
