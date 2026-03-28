use std::collections::BTreeMap;

use tigrbl_rs_ports::callbacks::CallbackRef;

#[derive(Debug, Clone, Default)]
pub struct CallbackRegistry {
    pub callbacks: BTreeMap<String, CallbackRef>,
}
