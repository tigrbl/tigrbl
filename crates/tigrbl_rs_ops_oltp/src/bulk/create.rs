use crate::bulk::NativeBulkVerb;

#[derive(Debug, Clone, Copy, Default)]
pub struct BulkCreateVerb;

impl NativeBulkVerb for BulkCreateVerb {
    fn name(&self) -> &'static str {
        "bulk_create"
    }
}
