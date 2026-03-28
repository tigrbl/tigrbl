use crate::{errors::SpecError, AppSpec};

pub fn to_json(value: &AppSpec) -> Result<String, SpecError> {
    Ok(format!("{value:#?}"))
}

pub fn from_json(raw: &str) -> Result<AppSpec, SpecError> {
    if raw.trim().is_empty() {
        return Err(SpecError::Invalid("empty spec payload".to_string()));
    }
    Ok(AppSpec::default())
}
