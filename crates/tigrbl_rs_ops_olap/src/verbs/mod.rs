pub mod aggregate;
pub mod group_by;

pub trait NativeOlapVerb {
    fn name(&self) -> &'static str;
    fn kind(&self) -> tigrbl_rs_spec::op::OpKind;
}
