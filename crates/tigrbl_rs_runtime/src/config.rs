#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct RuntimeConfig {
    pub service_name: String,
    pub enable_tracing: bool,
    pub enable_metrics: bool,
}
