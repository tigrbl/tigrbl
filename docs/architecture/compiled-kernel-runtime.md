# Compiled kernel runtime flow

The Rust flow is:

- spec authoring in Python
- canonical spec serialization into `tigrbl_rs_spec`
- kernel compilation in `tigrbl_rs_kernel`
- optimizer passes for fusion, compaction, dead-step elimination, and callback barriers
- runtime handle instantiation in `tigrbl_rs_runtime`
- request execution by the Rust executor
- fallback across FFI only for Python callback fences

`tigrbl_rs_kernel` owns plan construction and optimization. `tigrbl_rs_runtime` owns executor selection and transaction-safe invocation.
