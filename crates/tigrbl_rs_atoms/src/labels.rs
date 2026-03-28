use crate::phases::AtomPhase;

pub fn phase_label(phase: AtomPhase, name: &str) -> String {
    format!("{}::{name}", phase.as_str())
}
