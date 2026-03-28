#[derive(Debug, Clone, PartialEq, Eq)]
pub enum SpecError {
    Invalid(String),
    Serialization(String),
}

impl core::fmt::Display for SpecError {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        match self {
            Self::Invalid(msg) => write!(f, "invalid spec: {msg}"),
            Self::Serialization(msg) => write!(f, "serialization failure: {msg}"),
        }
    }
}

impl std::error::Error for SpecError {}
