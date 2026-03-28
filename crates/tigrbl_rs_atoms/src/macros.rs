#[macro_export]
macro_rules! declare_atom {
    ($name:expr, $phase:expr) => {{
        ($name, $phase)
    }};
}
