#[derive(Debug, Clone, PartialEq, Eq)]
pub enum AtomEvent {
    Started(String),
    Completed(String),
    Failed(String),
}
