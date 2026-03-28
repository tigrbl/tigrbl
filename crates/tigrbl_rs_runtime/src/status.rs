#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
pub enum RuntimeStatus {
    #[default]
    Ready,
    Running,
    Failed,
}
