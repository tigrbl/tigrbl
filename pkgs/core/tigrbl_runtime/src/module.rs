use pyo3::prelude::*;

use crate::{errors::RustResult, runtime_handle::PyRuntimeHandle};

fn into_py_err<T>(result: RustResult<T>) -> PyResult<T> {
    result.map_err(pyo3::exceptions::PyRuntimeError::new_err)
}

#[pyfunction]
fn normalize_spec(spec_json: &str) -> PyResult<String> {
    into_py_err(crate::normalize_spec(spec_json))
}

#[pyfunction]
fn compile_spec(spec_json: &str) -> PyResult<String> {
    into_py_err(crate::compile_spec(spec_json))
}

#[pyfunction]
fn create_runtime_handle(plan_json: &str) -> PyResult<PyRuntimeHandle> {
    into_py_err(crate::create_runtime_handle(plan_json).map(PyRuntimeHandle::from))
}

#[pyfunction]
fn register_python_callback(name: &str) -> PyResult<String> {
    into_py_err(crate::register_python_callback(name))
}

#[pyfunction]
fn register_python_atom(name: &str) -> PyResult<String> {
    into_py_err(crate::register_python_atom(name))
}

#[pyfunction]
fn register_python_hook(name: &str) -> PyResult<String> {
    into_py_err(crate::register_python_hook(name))
}

#[pyfunction]
fn register_python_handler(name: &str) -> PyResult<String> {
    into_py_err(crate::register_python_handler(name))
}

#[pyfunction]
fn register_python_engine(name: &str) -> PyResult<String> {
    into_py_err(crate::register_python_engine(name))
}

#[pyfunction]
fn ffi_boundary_events() -> PyResult<String> {
    serde_json::to_string(&crate::callback_registry::ffi_boundary_events())
        .map_err(|err| pyo3::exceptions::PyRuntimeError::new_err(err.to_string()))
}

#[pyfunction]
fn clear_ffi_boundary_events() {
    crate::callback_registry::clear_ffi_boundary_events();
}

#[pyfunction]
fn rust_available() -> bool {
    true
}

#[pyfunction]
fn compiled_extension_available() -> bool {
    true
}

#[pymodule]
pub fn _rust(_py: Python<'_>, module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PyRuntimeHandle>()?;
    module.add_function(wrap_pyfunction!(normalize_spec, module)?)?;
    module.add_function(wrap_pyfunction!(compile_spec, module)?)?;
    module.add_function(wrap_pyfunction!(create_runtime_handle, module)?)?;
    module.add_function(wrap_pyfunction!(register_python_callback, module)?)?;
    module.add_function(wrap_pyfunction!(register_python_atom, module)?)?;
    module.add_function(wrap_pyfunction!(register_python_hook, module)?)?;
    module.add_function(wrap_pyfunction!(register_python_handler, module)?)?;
    module.add_function(wrap_pyfunction!(register_python_engine, module)?)?;
    module.add_function(wrap_pyfunction!(ffi_boundary_events, module)?)?;
    module.add_function(wrap_pyfunction!(clear_ffi_boundary_events, module)?)?;
    module.add_function(wrap_pyfunction!(rust_available, module)?)?;
    module.add_function(wrap_pyfunction!(compiled_extension_available, module)?)?;
    Ok(())
}
