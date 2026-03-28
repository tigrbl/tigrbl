#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct RuntimeMetrics {
    pub requests_total: u64,
    pub callbacks_total: u64,
}
