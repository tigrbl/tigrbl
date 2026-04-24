use tigrbl_rs_kernel::plan::models::{KernelPlan, PlanBinding};
use tigrbl_rs_ports::errors::PortError;
use tigrbl_rs_spec::{request::RequestEnvelope, response::ResponseEnvelope, Value};

const DEFAULT_ROOT_ALIAS: &str = "__tigrbl_default_root__";

use crate::engine::{registry::EngineRegistry, resolver::EngineResolver};

pub struct RuntimeHandle {
    pub description: String,
    pub plan: KernelPlan,
    engine_registry: EngineRegistry,
    engine_resolver: EngineResolver,
}

impl RuntimeHandle {
    pub fn new(plan: KernelPlan) -> Self {
        let description = format!(
            "runtime handle for {} binding(s) in app {}",
            plan.bindings.len(),
            plan.app_name
        );
        let engine_registry = EngineRegistry::from_plan(&plan);
        Self {
            description,
            plan,
            engine_registry,
            engine_resolver: EngineResolver,
        }
    }

    pub fn describe(&self) -> String {
        self.description.clone()
    }

    pub fn execute_rest(&self, request: RequestEnvelope) -> Result<ResponseEnvelope, PortError> {
        self.execute_envelope("rest", request)
    }

    pub fn execute_jsonrpc(&self, request: RequestEnvelope) -> Result<ResponseEnvelope, PortError> {
        self.execute_envelope("jsonrpc", request)
    }

    pub fn execute_envelope(
        &self,
        transport: &str,
        request: RequestEnvelope,
    ) -> Result<ResponseEnvelope, PortError> {
        if self.should_use_default_root(transport, &request) {
            return Ok(default_root_response());
        }
        let binding = self.resolve_binding(transport, &request)?;
        if binding.engine_language != "rust" && binding.engine_callback.is_none() {
            return Err(PortError::Message(
                "python-backed engine missing callback".to_string(),
            ));
        }
        let engine = self
            .engine_resolver
            .resolve(&self.engine_registry, &binding.engine_kind)?;
        let session = engine.open()?;
        let tx = session.begin()?;
        let result = tx.execute(
            &binding.table,
            &binding.op_name,
            binding.op_kind.as_str(),
            &request,
        );

        match result {
            Ok(response) => {
                tx.commit()?;
                Ok(response)
            }
            Err(err) => {
                let _ = tx.rollback();
                Err(err)
            }
        }
    }

    fn resolve_binding<'a>(
        &'a self,
        transport: &str,
        request: &RequestEnvelope,
    ) -> Result<&'a PlanBinding, PortError> {
        let bindings = self
            .plan
            .bindings
            .iter()
            .filter(|binding| binding.transport == transport)
            .collect::<Vec<_>>();

        if !request.operation.is_empty() {
            if let Some(binding) = bindings.iter().copied().find(|binding| {
                binding.alias == request.operation
                    || binding.method_name == request.operation
                    || binding.op_name == request.operation
            }) {
                return Ok(binding);
            }
        }

        if !request.path.is_empty() {
            if let Some(binding) = bindings.iter().copied().find(|binding| {
                binding.path == request.path
                    && (request.method.is_empty() || binding.method == request.method)
            }) {
                return Ok(binding);
            }
        }

        bindings
            .into_iter()
            .find(|binding| binding.path == request.path)
            .ok_or_else(|| {
                PortError::Message(format!(
                    "no binding found for operation={} path={} transport={transport}",
                    request.operation, request.path
                ))
            })
    }

    fn should_use_default_root(&self, transport: &str, request: &RequestEnvelope) -> bool {
        if transport != "rest" || normalize_path(&request.path) != "/" {
            return false;
        }
        let method = if request.method.is_empty() {
            "GET"
        } else {
            request.method.as_str()
        };
        if !method.eq_ignore_ascii_case("GET") {
            return false;
        }
        !self.plan.bindings.iter().any(|binding| {
            binding.transport == "rest"
                && normalize_path(&binding.path) == "/"
                && binding.alias != DEFAULT_ROOT_ALIAS
        })
    }
}

fn normalize_path(path: &str) -> String {
    let trimmed = path.trim_end_matches('/');
    if trimmed.is_empty() {
        "/".to_string()
    } else {
        trimmed.to_string()
    }
}

fn default_root_response() -> ResponseEnvelope {
    ResponseEnvelope {
        status: 200,
        headers: Default::default(),
        body: Value::Object(
            [("ok".to_string(), Value::Bool(true))]
                .into_iter()
                .collect(),
        ),
    }
}
