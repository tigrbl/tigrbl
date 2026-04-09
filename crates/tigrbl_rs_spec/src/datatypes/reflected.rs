use std::collections::BTreeMap;

use crate::datatypes::{datatype_spec::DataTypeSpec, storage_type_ref::StorageTypeRef};
use crate::values::Value;

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct ReflectedDatatype {
    pub engine_kind: String,
    pub physical_name: String,
    pub logical_hint: Option<String>,
}

#[derive(Debug, Clone, Default)]
pub struct ReflectedTypeMapper;

impl ReflectedTypeMapper {
    fn mapping_for_engine(engine_kind: Option<&str>) -> BTreeMap<&'static str, &'static str> {
        let mut mapping = BTreeMap::from([
            ("varchar", "string"),
            ("text", "string"),
            ("string", "string"),
            ("integer", "integer"),
            ("int", "integer"),
            ("bigint", "integer"),
            ("float", "number"),
            ("double precision", "number"),
            ("numeric", "decimal"),
            ("decimal", "decimal"),
            ("boolean", "boolean"),
            ("bool", "boolean"),
            ("json", "json"),
            ("jsonb", "json"),
            ("uuid", "uuid"),
            ("bytea", "bytes"),
            ("blob", "bytes"),
            ("datetime", "datetime"),
            ("timestamp", "datetime"),
            ("timestamptz", "datetime"),
            ("date", "date"),
            ("time", "time"),
            ("interval", "duration"),
        ]);

        match engine_kind {
            Some("sqlite") => {
                mapping.insert("real", "number");
            }
            Some("postgres") => {
                mapping.insert("double precision", "number");
            }
            _ => {}
        }

        mapping
    }

    pub fn from_storage_ref(
        storage_ref: &StorageTypeRef,
        mode: &str,
        strict: bool,
    ) -> Result<DataTypeSpec, String> {
        let physical_name = storage_ref.physical_name.to_lowercase();
        let mapping = Self::mapping_for_engine(storage_ref.engine_kind.as_deref());
        let logical_name = mapping.get(physical_name.as_str()).copied();

        if strict && logical_name.is_none() {
            return Err(format!(
                "no reflected datatype mapping for {}:{}",
                storage_ref.engine_kind.as_deref().unwrap_or("unknown"),
                storage_ref.physical_name
            ));
        }

        let mut options = BTreeMap::new();
        if mode == "metadata_preserving" {
            options.insert(
                "reflected_physical_name".to_string(),
                Value::String(storage_ref.physical_name.clone()),
            );
            if let Some(engine_kind) = &storage_ref.engine_kind {
                options.insert(
                    "reflected_engine_kind".to_string(),
                    Value::String(engine_kind.clone()),
                );
            }
        }

        let logical_name = logical_name.unwrap_or("object");
        if logical_name == "object" {
            options.insert(
                "downgraded_from_physical_name".to_string(),
                Value::String(storage_ref.physical_name.clone()),
            );
        }

        Ok(DataTypeSpec {
            logical_name: logical_name.to_string(),
            nullable: false,
            options,
        })
    }
}
