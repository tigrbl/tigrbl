use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct CollectOutAtom;

impl AtomStep for CollectOutAtom {
    fn name(&self) -> &'static str {
        "schema.collect_out"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Schema
    }
}
