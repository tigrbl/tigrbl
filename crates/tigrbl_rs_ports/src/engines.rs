use crate::{errors::PortResult, sessions::SessionPort};

pub trait EnginePort: Send + Sync {
    fn kind(&self) -> &str;
    fn open(&self) -> PortResult<Box<dyn SessionPort>>;
}
