use std::collections::BTreeMap;

use crate::datatypes::storage_type_ref::StorageTypeRef;

fn builtin_engine_mappings() -> BTreeMap<String, BTreeMap<String, StorageTypeRef>> {
    let mut out = BTreeMap::new();

    let sqlite = BTreeMap::from([
        (
            "string".to_string(),
            StorageTypeRef::new("TEXT", Some("sqlite")),
        ),
        (
            "integer".to_string(),
            StorageTypeRef::new("INTEGER", Some("sqlite")),
        ),
        (
            "number".to_string(),
            StorageTypeRef::new("REAL", Some("sqlite")),
        ),
        (
            "decimal".to_string(),
            StorageTypeRef::new("NUMERIC", Some("sqlite")),
        ),
        (
            "boolean".to_string(),
            StorageTypeRef::new("BOOLEAN", Some("sqlite")),
        ),
        (
            "bytes".to_string(),
            StorageTypeRef::new("BLOB", Some("sqlite")),
        ),
        (
            "json".to_string(),
            StorageTypeRef::new("JSON", Some("sqlite")),
        ),
        (
            "object".to_string(),
            StorageTypeRef::new("JSON", Some("sqlite")),
        ),
        (
            "array".to_string(),
            StorageTypeRef::new("JSON", Some("sqlite")),
        ),
        (
            "uuid".to_string(),
            StorageTypeRef::new("TEXT", Some("sqlite")),
        ),
        (
            "ulid".to_string(),
            StorageTypeRef::new("TEXT", Some("sqlite")),
        ),
    ]);
    out.insert("sqlite".to_string(), sqlite);

    let postgres = BTreeMap::from([
        (
            "string".to_string(),
            StorageTypeRef::new("TEXT", Some("postgres")),
        ),
        (
            "integer".to_string(),
            StorageTypeRef::new("BIGINT", Some("postgres")),
        ),
        (
            "number".to_string(),
            StorageTypeRef::new("DOUBLE PRECISION", Some("postgres")),
        ),
        (
            "decimal".to_string(),
            StorageTypeRef::new("NUMERIC", Some("postgres")),
        ),
        (
            "boolean".to_string(),
            StorageTypeRef::new("BOOLEAN", Some("postgres")),
        ),
        (
            "bytes".to_string(),
            StorageTypeRef::new("BYTEA", Some("postgres")),
        ),
        (
            "json".to_string(),
            StorageTypeRef::new("JSONB", Some("postgres")),
        ),
        (
            "object".to_string(),
            StorageTypeRef::new("JSONB", Some("postgres")),
        ),
        (
            "array".to_string(),
            StorageTypeRef::new("JSONB", Some("postgres")),
        ),
        (
            "uuid".to_string(),
            StorageTypeRef::new("UUID", Some("postgres")),
        ),
        (
            "ulid".to_string(),
            StorageTypeRef::new("UUID", Some("postgres")),
        ),
    ]);
    out.insert("postgres".to_string(), postgres);

    let dataframe = BTreeMap::from([
        (
            "string".to_string(),
            StorageTypeRef::new("string", Some("dataframe")),
        ),
        (
            "integer".to_string(),
            StorageTypeRef::new("int64", Some("dataframe")),
        ),
        (
            "number".to_string(),
            StorageTypeRef::new("float64", Some("dataframe")),
        ),
        (
            "decimal".to_string(),
            StorageTypeRef::new("object", Some("dataframe")),
        ),
        (
            "boolean".to_string(),
            StorageTypeRef::new("bool", Some("dataframe")),
        ),
        (
            "bytes".to_string(),
            StorageTypeRef::new("bytes", Some("dataframe")),
        ),
        (
            "datetime".to_string(),
            StorageTypeRef::new("datetime64[ns]", Some("dataframe")),
        ),
        (
            "date".to_string(),
            StorageTypeRef::new("datetime64[ns]", Some("dataframe")),
        ),
        (
            "json".to_string(),
            StorageTypeRef::new("object", Some("dataframe")),
        ),
    ]);
    out.insert("dataframe".to_string(), dataframe);

    let cache = BTreeMap::from([
        (
            "string".to_string(),
            StorageTypeRef::new("string", Some("cache")),
        ),
        (
            "integer".to_string(),
            StorageTypeRef::new("string", Some("cache")),
        ),
        (
            "number".to_string(),
            StorageTypeRef::new("string", Some("cache")),
        ),
        (
            "decimal".to_string(),
            StorageTypeRef::new("string", Some("cache")),
        ),
        (
            "boolean".to_string(),
            StorageTypeRef::new("string", Some("cache")),
        ),
        (
            "bytes".to_string(),
            StorageTypeRef::new("bytes", Some("cache")),
        ),
        (
            "json".to_string(),
            StorageTypeRef::new("json", Some("cache")),
        ),
        (
            "object".to_string(),
            StorageTypeRef::new("json", Some("cache")),
        ),
        (
            "array".to_string(),
            StorageTypeRef::new("json", Some("cache")),
        ),
    ]);
    out.insert("cache".to_string(), cache);

    out
}

#[derive(Debug, Clone, Default)]
pub struct EngineDatatypeRegistry {
    pub lowerers_by_engine: BTreeMap<String, BTreeMap<String, StorageTypeRef>>,
}

impl EngineDatatypeRegistry {
    pub fn with_builtins() -> Self {
        Self {
            lowerers_by_engine: builtin_engine_mappings(),
        }
    }

    pub fn register(
        &mut self,
        engine_kind: impl Into<String>,
        logical_name: impl Into<String>,
        storage_type: StorageTypeRef,
    ) {
        self.lowerers_by_engine
            .entry(engine_kind.into())
            .or_default()
            .insert(logical_name.into(), storage_type);
    }

    pub fn lower(&self, engine_kind: &str, logical_name: &str) -> Option<StorageTypeRef> {
        self.lowerers_by_engine
            .get(engine_kind)
            .and_then(|entries| entries.get(logical_name))
            .cloned()
    }

    pub fn lower_strict(
        &self,
        engine_kind: &str,
        logical_name: &str,
    ) -> Result<StorageTypeRef, String> {
        self.lower(engine_kind, logical_name).ok_or_else(|| {
            format!("engine '{engine_kind}' does not support logical datatype '{logical_name}'")
        })
    }
}
