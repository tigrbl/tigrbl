use crate::bulk::NativeBulkVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct BulkReplaceVerb;

impl NativeBulkVerb for BulkReplaceVerb {
    fn name(&self) -> &'static str {
        "bulk_replace"
    }
}
