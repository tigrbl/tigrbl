pub mod clear;
pub mod count;
pub mod create;
pub mod delete;
pub mod exists;
pub mod list;
pub mod merge;
pub mod read;
pub mod replace;
pub mod update;

pub trait NativeOltpVerb {
    fn name(&self) -> &'static str;
    fn kind(&self) -> tigrbl_rs_spec::op::OpKind;
}
