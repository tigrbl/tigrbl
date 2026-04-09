use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerDownloadAtom;

impl AtomStep for HandlerDownloadAtom {
    fn name(&self) -> &'static str {
        "sys.handler_download"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
