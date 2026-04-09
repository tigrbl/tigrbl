use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerUploadAtom;

impl AtomStep for HandlerUploadAtom {
    fn name(&self) -> &'static str {
        "sys.handler_upload"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
