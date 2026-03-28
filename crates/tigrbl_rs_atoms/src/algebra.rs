use crate::phases::AtomPhase;

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct PhaseAlgebra {
    pub phases: Vec<AtomPhase>,
}
