#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum AtomPhase {
    Dep,
    Ingress,
    Dispatch,
    Schema,
    Wire,
    Resolve,
    Storage,
    Emit,
    Refresh,
    Response,
    Egress,
    Out,
    Error,
    Sys,
}

impl AtomPhase {
    pub const ALL: [AtomPhase; 14] = [
        AtomPhase::Dep,
        AtomPhase::Ingress,
        AtomPhase::Dispatch,
        AtomPhase::Schema,
        AtomPhase::Wire,
        AtomPhase::Resolve,
        AtomPhase::Storage,
        AtomPhase::Emit,
        AtomPhase::Refresh,
        AtomPhase::Response,
        AtomPhase::Egress,
        AtomPhase::Out,
        AtomPhase::Error,
        AtomPhase::Sys,
    ];

    pub fn all() -> &'static [AtomPhase] {
        &Self::ALL
    }

    pub fn as_str(self) -> &'static str {
        match self {
            Self::Dep => "dep",
            Self::Ingress => "ingress",
            Self::Dispatch => "dispatch",
            Self::Schema => "schema",
            Self::Wire => "wire",
            Self::Resolve => "resolve",
            Self::Storage => "storage",
            Self::Emit => "emit",
            Self::Refresh => "refresh",
            Self::Response => "response",
            Self::Egress => "egress",
            Self::Out => "out",
            Self::Error => "error",
            Self::Sys => "sys",
        }
    }
}
