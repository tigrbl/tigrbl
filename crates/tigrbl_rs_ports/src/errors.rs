#[derive(Debug, Clone, PartialEq, Eq)]
pub enum PortError {
    NotImplemented(String),
    Message(String),
}

pub type PortResult<T> = Result<T, PortError>;

impl PortError {
    pub fn not_implemented(name: impl Into<String>) -> Self {
        Self::NotImplemented(name.into())
    }
}

impl core::fmt::Display for PortError {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        match self {
            Self::NotImplemented(msg) => write!(f, "not implemented: {msg}"),
            Self::Message(msg) => write!(f, "port error: {msg}"),
        }
    }
}

impl std::error::Error for PortError {}
