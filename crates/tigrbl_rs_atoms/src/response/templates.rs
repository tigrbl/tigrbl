use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct TemplatesAtom;

impl AtomStep for TemplatesAtom {
    fn name(&self) -> &'static str {
        "response.templates"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Response
    }
}
