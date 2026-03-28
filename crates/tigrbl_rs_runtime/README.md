        # tigrbl_rs_runtime

        Native runtime, executor, callback fence, engine resolution, and transaction lifecycle management for compiled kernel plans.

        ## Owns

        - runtime handles and config
- executor selection and phase invocation
- callback fences and engine resolution

        ## Does not own

        - spec authoring
- compile-time plan optimization
- CRUD semantic definition
