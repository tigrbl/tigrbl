use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct CollectInAtom;

impl AtomStep for CollectInAtom {
    fn name(&self) -> &'static str {
        "schema.collect_in"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Schema
    }
}
