        # tigrbl_rs_kernel

        Rust-native compile pipeline from canonical spec into a packed, optimizable kernel plan.

        ## Owns

        - route and opview lowering
- phase-chain assembly
- packed plan model and optimizer passes

        ## Does not own

        - live request execution
- DB sessions and transaction ownership
- Python object invocation
