use crate::values::Value;

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub enum HookPhase {
    #[default]
    PreTxBegin,
    StartTx,
    PreHandler,
    Handler,
    PostHandler,
    PreCommit,
    EndTx,
    PostCommit,
    PostResponse,
    OnError,
    Rollback,
    Custom,
}

impl HookPhase {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::PreTxBegin => "pre_tx_begin",
            Self::StartTx => "start_tx",
            Self::PreHandler => "pre_handler",
            Self::Handler => "handler",
            Self::PostHandler => "post_handler",
            Self::PreCommit => "pre_commit",
            Self::EndTx => "end_tx",
            Self::PostCommit => "post_commit",
            Self::PostResponse => "post_response",
            Self::OnError => "on_error",
            Self::Rollback => "rollback",
            Self::Custom => "custom",
        }
    }
}

#[derive(Debug, Clone, Default, PartialEq)]
pub struct HookSpec {
    pub name: String,
    pub phase: HookPhase,
    pub metadata: Value,
}
