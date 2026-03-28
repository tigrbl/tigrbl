use crate::bulk::NativeBulkVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct BulkMergeVerb;

impl NativeBulkVerb for BulkMergeVerb {
    fn name(&self) -> &'static str {
        "bulk_merge"
    }
}
