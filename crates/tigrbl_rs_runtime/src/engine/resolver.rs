use tigrbl_rs_ports::{engines::EnginePort, errors::PortError};

use crate::engine::registry::EngineRegistry;

#[derive(Default)]
pub struct EngineResolver;

impl EngineResolver {
    pub fn resolve<'a>(
        &self,
        registry: &'a EngineRegistry,
        kind: &str,
    ) -> Result<&'a dyn EnginePort, PortError> {
        registry
            .get(kind)
            .ok_or_else(|| PortError::Message(format!("unknown engine kind: {kind}")))
    }
}
