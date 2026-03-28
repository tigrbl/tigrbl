#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct RequestField {
    pub name: String,
    pub required: bool,
}

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct ResponseField {
    pub name: String,
    pub projected: bool,
}
