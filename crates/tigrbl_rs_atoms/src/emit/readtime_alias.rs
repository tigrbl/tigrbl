use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct ReadtimeAliasAtom;

impl AtomStep for ReadtimeAliasAtom {
    fn name(&self) -> &'static str {
        "emit.readtime_alias"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Emit
    }
}
