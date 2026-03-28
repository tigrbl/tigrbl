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
    let normalized = spec_codec::normalize_spec(spec_json)?;
    Ok(format!("compiled-spec:{}", normalized.len()))
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
