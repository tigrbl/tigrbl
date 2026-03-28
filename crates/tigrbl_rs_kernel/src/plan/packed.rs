#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct PackedPlan {
    pub segments: usize,
    pub hot_paths: usize,
    pub fused_steps: usize,
}

impl PackedPlan {
    pub fn from_binding_count(binding_count: usize) -> Self {
        Self {
            segments: binding_count,
            hot_paths: binding_count.min(1),
            fused_steps: binding_count,
        }
    }
}
