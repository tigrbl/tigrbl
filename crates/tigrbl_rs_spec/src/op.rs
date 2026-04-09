#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub enum OpKind {
    #[default]
    Create,
    Read,
    Update,
    Replace,
    Merge,
    Delete,
    List,
    Clear,
    Count,
    Exists,
    BulkCreate,
    BulkUpdate,
    BulkReplace,
    BulkMerge,
    BulkDelete,
    Aggregate,
    GroupBy,
    Publish,
    Subscribe,
    Tail,
    Upload,
    Download,
    AppendChunk,
    SendDatagram,
    Checkpoint,
    Custom,
}

impl OpKind {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Create => "create",
            Self::Read => "read",
            Self::Update => "update",
            Self::Replace => "replace",
            Self::Merge => "merge",
            Self::Delete => "delete",
            Self::List => "list",
            Self::Clear => "clear",
            Self::Count => "count",
            Self::Exists => "exists",
            Self::BulkCreate => "bulk_create",
            Self::BulkUpdate => "bulk_update",
            Self::BulkReplace => "bulk_replace",
            Self::BulkMerge => "bulk_merge",
            Self::BulkDelete => "bulk_delete",
            Self::Aggregate => "aggregate",
            Self::GroupBy => "group_by",
            Self::Publish => "publish",
            Self::Subscribe => "subscribe",
            Self::Tail => "tail",
            Self::Upload => "upload",
            Self::Download => "download",
            Self::AppendChunk => "append_chunk",
            Self::SendDatagram => "send_datagram",
            Self::Checkpoint => "checkpoint",
            Self::Custom => "custom",
        }
    }

    pub fn is_bulk(&self) -> bool {
        matches!(
            self,
            Self::BulkCreate
                | Self::BulkUpdate
                | Self::BulkReplace
                | Self::BulkMerge
                | Self::BulkDelete
        )
    }
}

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct OpSpec {
    pub kind: OpKind,
    pub name: String,
    pub route: Option<String>,
}
