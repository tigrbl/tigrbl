#[derive(Debug, Clone, Default, PartialEq)]
pub struct Versioned<T> {
    pub version: String,
    pub payload: T,
}
