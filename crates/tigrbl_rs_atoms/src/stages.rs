#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum StageKind {
    Prepare,
    Validate,
    Resolve,
    Handle,
    Finalize,
}
