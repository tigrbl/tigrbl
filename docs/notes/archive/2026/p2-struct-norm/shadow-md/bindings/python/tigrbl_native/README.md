        # tigrbl_native

        PyO3 / maturin bridge used to serialize Python-authored specs into Rust-native IR, compile native plans, and instantiate native runtime handles.

        ## Owns

        - spec normalization and FFI entrypoints
- callback registration descriptors
- runtime handle creation

        ## Does not own

        - kernel optimizer ownership
- engine implementation logic
- long-term business logic
