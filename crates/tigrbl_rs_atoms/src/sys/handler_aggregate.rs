use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct HandlerAggregateAtom;

impl AtomStep for HandlerAggregateAtom {
    fn name(&self) -> &'static str {
        "sys.handler_aggregate"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Sys
    }
}
