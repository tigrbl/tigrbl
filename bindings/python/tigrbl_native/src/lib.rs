mod callback_registry;
mod errors;
mod py_atoms;
mod py_engines;
mod py_handlers;
mod py_hooks;
mod runtime_handle;
mod spec_codec;

pub use errors::NativeResult;
pub use runtime_handle::RuntimeHandle;

pub fn normalize_spec(spec_json: &str) -> NativeResult<String> {
    spec_codec::normalize_spec(spec_json)
}

pub fn compile_spec(spec_json: &str) -> NativeResult<String> {
    let spec = spec_codec::decode_spec(spec_json)?;
    let plan = tigrbl_rs_kernel::KernelCompiler::default().compile(&spec);
    serde_json::to_string(&serde_json::json!({
        "description": format!(
            "compiled native plan for {} with {} binding(s)",
            plan.app_name,
            plan.bindings.len()
        ),
        "app_name": plan.app_name,
        "engine_kind": plan.engine_kind,
        "binding_count": plan.bindings.len(),
        "route_count": plan.routes.len(),
        "packed": plan.packed.as_ref().map(|packed| serde_json::json!({
            "segments": packed.segments,
            "hot_paths": packed.hot_paths,
            "fused_steps": packed.fused_steps,
            "routes": packed.routes,
        })),
    }))
    .map_err(|err| err.to_string())
}

pub fn create_runtime_handle(spec_json: &str) -> NativeResult<runtime_handle::RuntimeHandle> {
    runtime_handle::create_runtime_handle(spec_json)
}

pub fn register_python_callback(name: &str) -> NativeResult<String> {
    Ok(callback_registry::descriptor("python-callback", name))
}

pub fn register_python_atom(name: &str) -> NativeResult<String> {
    Ok(py_atoms::register_python_atom(name))
}

pub fn register_python_hook(name: &str) -> NativeResult<String> {
    Ok(py_hooks::register_python_hook(name))
}

pub fn register_python_handler(name: &str) -> NativeResult<String> {
    Ok(py_handlers::register_python_handler(name))
}

pub fn register_python_engine(name: &str) -> NativeResult<String> {
    Ok(py_engines::register_python_engine(name))
}
