use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerSendDatagramAtom;

impl AtomStep for HandlerSendDatagramAtom {
    fn name(&self) -> &'static str {
        "sys.handler_send_datagram"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
