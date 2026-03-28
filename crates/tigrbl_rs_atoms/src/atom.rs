use crate::phases::AtomPhase;

pub trait AtomStep: Send + Sync {
    fn name(&self) -> &'static str;
    fn phase(&self) -> AtomPhase;
}
