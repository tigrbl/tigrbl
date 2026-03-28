use crate::errors::NativeResult;

pub fn normalize_spec(spec_json: &str) -> NativeResult<String> {
    let trimmed = spec_json.trim();
    if trimmed.is_empty() {
        return Err("empty spec payload".to_string());
    }
    Ok(trimmed.to_string())
}
