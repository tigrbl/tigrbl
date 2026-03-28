use crate::atom::AtomStep;
use crate::phases::AtomPhase;

#[derive(Debug, Clone, Copy, Default)]
pub struct ParamResolverAtom;

impl AtomStep for ParamResolverAtom {
    fn name(&self) -> &'static str {
        "dep.param_resolver"
    }

    fn phase(&self) -> AtomPhase {
        AtomPhase::Dep
    }
}
