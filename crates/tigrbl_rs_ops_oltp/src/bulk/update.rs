use crate::bulk::NativeBulkVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct BulkUpdateVerb;

impl NativeBulkVerb for BulkUpdateVerb {
    fn name(&self) -> &'static str {
        "bulk_update"
    }
}
