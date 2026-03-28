use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct TemplateAtom;

impl AtomStep for TemplateAtom {
    fn name(&self) -> &'static str {
        "response.template"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Response
    }
}
