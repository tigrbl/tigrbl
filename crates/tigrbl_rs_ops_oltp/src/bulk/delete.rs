use crate::bulk::NativeBulkVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct BulkDeleteVerb;

impl NativeBulkVerb for BulkDeleteVerb {
    fn name(&self) -> &'static str {
        "bulk_delete"
    }
}
