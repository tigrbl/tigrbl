        # tigrbl_rs_ops_oltp

        Rust-native CRUD and bulk operation semantics used by sys handler atoms and the native runtime.

        ## Owns

        - CRUD verbs and bulk verbs
- normalization, defaults, filters, patch/merge shaping
- native handler registry

        ## Does not own

        - phase algebra
- kernel plan compilation
- runtime executor ownership
