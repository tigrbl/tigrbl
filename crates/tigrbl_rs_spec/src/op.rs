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
    BulkCreate,
    BulkUpdate,
    BulkReplace,
    BulkMerge,
    BulkDelete,
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
            Self::BulkCreate => "bulk_create",
            Self::BulkUpdate => "bulk_update",
            Self::BulkReplace => "bulk_replace",
            Self::BulkMerge => "bulk_merge",
            Self::BulkDelete => "bulk_delete",
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
