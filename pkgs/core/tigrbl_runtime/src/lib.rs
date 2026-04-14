mod callback_registry;
mod errors;
mod module;
mod py_atoms;
mod py_engines;
mod py_handlers;
mod py_hooks;
mod py_request;
mod py_response;
mod py_runtime;
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
    callback_registry::record_event(
        "compile_spec",
        serde_json::json!({"app_name": plan.app_name, "bindings": plan.bindings.len()}),
    );
    runtime_handle::encode_plan(&plan)
}

pub fn create_runtime_handle(spec_json: &str) -> NativeResult<runtime_handle::RuntimeHandle> {
    runtime_handle::create_runtime_handle(spec_json)
}

pub fn register_python_callback(name: &str) -> NativeResult<String> {
    callback_registry::record_event(
        "register_python_callback",
        serde_json::json!({"name": name}),
    );
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
