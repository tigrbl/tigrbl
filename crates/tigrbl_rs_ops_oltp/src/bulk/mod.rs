pub mod create;
pub mod delete;
pub mod merge;
pub mod replace;
pub mod update;

pub trait NativeBulkVerb {
    fn name(&self) -> &'static str;
}
