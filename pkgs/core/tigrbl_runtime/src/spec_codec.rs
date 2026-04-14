use crate::errors::NativeResult;
use tigrbl_rs_spec::{serde::json, AppSpec};

pub fn normalize_spec(spec_json: &str) -> NativeResult<String> {
    let spec = decode_spec(spec_json)?;
    json::to_json(&spec).map_err(|err| err.to_string())
}

pub fn decode_spec(spec_json: &str) -> NativeResult<AppSpec> {
    let trimmed = spec_json.trim();
    if trimmed.is_empty() {
        return Err("empty spec payload".to_string());
    }
    json::from_json(trimmed).map_err(|err| err.to_string())
}
