use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct RenderAtom;

impl AtomStep for RenderAtom {
    fn name(&self) -> &'static str {
        "response.render"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Response
    }
}
