use std::{collections::BTreeMap, sync::Mutex};

use rusqlite::{params, Connection, OptionalExtension};
use tigrbl_rs_ports::{
    errors::{PortError, PortResult},
    transactions::TransactionPort,
};
use tigrbl_rs_spec::{request::RequestEnvelope, response::ResponseEnvelope, values::Value};

const DEFAULT_ROOT_ALIAS: &str = "__tigrbl_default_root__";

const SCHEMA_SQL: &str = "CREATE TABLE IF NOT EXISTS _tigrbl_rows (
    table_name TEXT NOT NULL,
    row_key TEXT,
    row_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tigrbl_rows_table_key
    ON _tigrbl_rows(table_name, row_key);";

pub struct SqliteTransaction {
    connection: Mutex<Connection>,
    tables: Vec<String>,
}

impl SqliteTransaction {
    pub fn begin(path: String, tables: Vec<String>) -> PortResult<Self> {
        let is_memory = is_memory_path(&path);
        let connection = Connection::open(path).map_err(sqlite_error)?;
        if is_memory {
            initialize_schema_on(&connection, &tables)?;
        }
        connection
            .execute_batch("BEGIN IMMEDIATE;")
            .map_err(sqlite_error)?;
        Ok(Self {
            connection: Mutex::new(connection),
            tables,
        })
    }
}

pub fn initialize_schema(path: &str, tables: &[String]) -> PortResult<()> {
    if is_memory_path(path) {
        return Ok(());
    }
    let connection = Connection::open(path).map_err(sqlite_error)?;
    initialize_schema_on(&connection, tables)
}

fn initialize_schema_on(connection: &Connection, tables: &[String]) -> PortResult<()> {
    connection.execute_batch(SCHEMA_SQL).map_err(sqlite_error)?;
    for table in tables {
        create_relational_table(connection, table)?;
    }
    Ok(())
}

fn is_memory_path(path: &str) -> bool {
    path == ":memory:"
}

impl TransactionPort for SqliteTransaction {
    fn commit(&self) -> PortResult<()> {
        let connection = self.connection()?;
        connection.execute_batch("COMMIT").map_err(sqlite_error)
    }

    fn rollback(&self) -> PortResult<()> {
        let connection = self.connection()?;
        connection.execute_batch("ROLLBACK").map_err(sqlite_error)
    }

    fn execute(
        &self,
        table: &str,
        operation: &str,
        kind: &str,
        request: &RequestEnvelope,
    ) -> PortResult<ResponseEnvelope> {
        if kind == "read" && (table == DEFAULT_ROOT_ALIAS || operation == DEFAULT_ROOT_ALIAS) {
            return Ok(default_root_response());
        }
        match kind {
            "create" => {
                let row = body_object(&request.body)?;
                let connection = self.connection()?;
                if self.uses_relational_table(table) {
                    return create_relational_row(&connection, table, row);
                }
                let row_key = find_id(request).map(value_key);
                let row_json = serde_json::to_string(&value_to_json(&Value::Object(row.clone())))
                    .map_err(json_error)?;
                connection
                    .execute(
                        "INSERT INTO _tigrbl_rows(table_name, row_key, row_json)
                         VALUES (?1, ?2, ?3)",
                        params![table, row_key, row_json],
                    )
                    .map_err(sqlite_error)?;
                Ok(ResponseEnvelope {
                    status: 201,
                    headers: BTreeMap::new(),
                    body: Value::Object(row),
                })
            }
            "read" => {
                let row_key = find_id(request)
                    .map(value_key)
                    .ok_or_else(|| PortError::Message("missing id for read".to_string()))?;
                let connection = self.connection()?;
                if self.uses_relational_table(table) {
                    let row = select_relational_row(&connection, table, &row_key)?
                        .ok_or_else(|| PortError::Message(format!("row not found in {table}")))?;
                    return Ok(ResponseEnvelope {
                        status: 200,
                        headers: BTreeMap::new(),
                        body: Value::Object(row),
                    });
                }
                let row = select_row(&connection, table, &row_key)?
                    .ok_or_else(|| PortError::Message(format!("row not found in {table}")))?;
                Ok(ResponseEnvelope {
                    status: 200,
                    headers: BTreeMap::new(),
                    body: Value::Object(row),
                })
            }
            "update" | "replace" => {
                let row_key = find_id(request)
                    .map(value_key)
                    .ok_or_else(|| PortError::Message(format!("missing id for {kind}")))?;
                let body = body_object(&request.body)?;
                let connection = self.connection()?;
                update_row(&connection, table, &row_key, &body)?;
                Ok(ResponseEnvelope {
                    status: 200,
                    headers: BTreeMap::new(),
                    body: Value::Object(body),
                })
            }
            "merge" => {
                let row_key = find_id(request)
                    .map(value_key)
                    .ok_or_else(|| PortError::Message("missing id for merge".to_string()))?;
                let connection = self.connection()?;
                let mut row = select_row(&connection, table, &row_key)?
                    .ok_or_else(|| PortError::Message(format!("row not found in {table}")))?;
                for (key, value) in body_object(&request.body)? {
                    row.insert(key, value);
                }
                update_row(&connection, table, &row_key, &row)?;
                Ok(ResponseEnvelope {
                    status: 200,
                    headers: BTreeMap::new(),
                    body: Value::Object(row),
                })
            }
            "delete" => {
                let row_key = find_id(request)
                    .map(value_key)
                    .ok_or_else(|| PortError::Message("missing id for delete".to_string()))?;
                let connection = self.connection()?;
                let row = select_row(&connection, table, &row_key)?
                    .ok_or_else(|| PortError::Message(format!("row not found in {table}")))?;
                connection
                    .execute(
                        "DELETE FROM _tigrbl_rows
                         WHERE rowid = (
                            SELECT rowid FROM _tigrbl_rows
                            WHERE table_name = ?1 AND row_key = ?2
                            ORDER BY rowid LIMIT 1
                         )",
                        params![table, row_key],
                    )
                    .map_err(sqlite_error)?;
                Ok(ResponseEnvelope {
                    status: 200,
                    headers: BTreeMap::new(),
                    body: Value::Object(row),
                })
            }
            "list" => {
                let connection = self.connection()?;
                if self.uses_relational_table(table) {
                    return list_relational_rows(&connection, table);
                }
                let mut statement = connection
                    .prepare(
                        "SELECT row_json FROM _tigrbl_rows
                         WHERE table_name = ?1 ORDER BY rowid",
                    )
                    .map_err(sqlite_error)?;
                let rows = statement
                    .query_map(params![table], |row| row.get::<_, String>(0))
                    .map_err(sqlite_error)?
                    .map(|item| {
                        let raw = item.map_err(sqlite_error)?;
                        value_from_json_str(&raw).and_then(value_object)
                    })
                    .collect::<PortResult<Vec<_>>>()?;
                Ok(ResponseEnvelope {
                    status: 200,
                    headers: BTreeMap::new(),
                    body: Value::Array(rows.into_iter().map(Value::Object).collect()),
                })
            }
            _ => Err(PortError::not_implemented(kind)),
        }
    }
}

impl SqliteTransaction {
    fn connection(&self) -> PortResult<std::sync::MutexGuard<'_, Connection>> {
        self.connection
            .lock()
            .map_err(|_| PortError::Message("sqlite connection mutex poisoned".to_string()))
    }

    fn uses_relational_table(&self, table: &str) -> bool {
        self.tables.iter().any(|item| item == table)
    }
}

fn create_relational_table(connection: &Connection, table: &str) -> PortResult<()> {
    let table = quote_identifier(table)?;
    connection
        .execute_batch(&format!(
            "CREATE TABLE IF NOT EXISTS {table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );"
        ))
        .map_err(sqlite_error)
}

fn create_relational_row(
    connection: &Connection,
    table: &str,
    row: BTreeMap<String, Value>,
) -> PortResult<ResponseEnvelope> {
    let name = match row.get("name") {
        Some(Value::String(value)) => value.clone(),
        _ => {
            return Err(PortError::Message(
                "request body must include string field name".to_string(),
            ))
        }
    };
    let table = quote_identifier(table)?;
    connection
        .execute(
            &format!("INSERT INTO {table}(name) VALUES (?1)"),
            params![name],
        )
        .map_err(sqlite_error)?;
    let mut response = BTreeMap::new();
    response.insert(
        "id".to_string(),
        Value::Integer(connection.last_insert_rowid()),
    );
    response.insert("name".to_string(), Value::String(name));
    Ok(ResponseEnvelope {
        status: 201,
        headers: BTreeMap::new(),
        body: Value::Object(response),
    })
}

fn default_root_response() -> ResponseEnvelope {
    ResponseEnvelope {
        status: 200,
        headers: BTreeMap::new(),
        body: Value::Object(
            [("ok".to_string(), Value::Bool(true))]
                .into_iter()
                .collect(),
        ),
    }
}

fn select_relational_row(
    connection: &Connection,
    table: &str,
    row_key: &str,
) -> PortResult<Option<BTreeMap<String, Value>>> {
    let table = quote_identifier(table)?;
    let raw = connection
        .query_row(
            &format!("SELECT id, name FROM {table} WHERE id = ?1 LIMIT 1"),
            params![row_key],
            |row| Ok((row.get::<_, i64>(0)?, row.get::<_, String>(1)?)),
        )
        .optional()
        .map_err(sqlite_error)?;
    Ok(raw.map(|(id, name)| {
        BTreeMap::from([
            ("id".to_string(), Value::Integer(id)),
            ("name".to_string(), Value::String(name)),
        ])
    }))
}

fn list_relational_rows(connection: &Connection, table: &str) -> PortResult<ResponseEnvelope> {
    let table = quote_identifier(table)?;
    let mut statement = connection
        .prepare(&format!("SELECT id, name FROM {table} ORDER BY id"))
        .map_err(sqlite_error)?;
    let rows = statement
        .query_map([], |row| {
            Ok((row.get::<_, i64>(0)?, row.get::<_, String>(1)?))
        })
        .map_err(sqlite_error)?
        .map(|item| {
            let (id, name) = item.map_err(sqlite_error)?;
            Ok(Value::Object(BTreeMap::from([
                ("id".to_string(), Value::Integer(id)),
                ("name".to_string(), Value::String(name)),
            ])))
        })
        .collect::<PortResult<Vec<_>>>()?;
    Ok(ResponseEnvelope {
        status: 200,
        headers: BTreeMap::new(),
        body: Value::Array(rows),
    })
}

fn quote_identifier(identifier: &str) -> PortResult<String> {
    if identifier.is_empty()
        || !identifier
            .chars()
            .all(|item| item.is_ascii_alphanumeric() || item == '_')
    {
        return Err(PortError::Message(format!(
            "unsupported sqlite identifier {identifier}"
        )));
    }
    Ok(format!("\"{}\"", identifier.replace('"', "\"\"")))
}

fn select_row(
    connection: &Connection,
    table: &str,
    row_key: &str,
) -> PortResult<Option<BTreeMap<String, Value>>> {
    let raw = connection
        .query_row(
            "SELECT row_json FROM _tigrbl_rows
             WHERE table_name = ?1 AND row_key = ?2
             ORDER BY rowid LIMIT 1",
            params![table, row_key],
            |row| row.get::<_, String>(0),
        )
        .optional()
        .map_err(sqlite_error)?;
    raw.map(|value| value_from_json_str(&value).and_then(value_object))
        .transpose()
}

fn update_row(
    connection: &Connection,
    table: &str,
    row_key: &str,
    row: &BTreeMap<String, Value>,
) -> PortResult<()> {
    let row_json =
        serde_json::to_string(&value_to_json(&Value::Object(row.clone()))).map_err(json_error)?;
    let changed = connection
        .execute(
            "UPDATE _tigrbl_rows SET row_json = ?3
             WHERE rowid = (
                SELECT rowid FROM _tigrbl_rows
                WHERE table_name = ?1 AND row_key = ?2
                ORDER BY rowid LIMIT 1
             )",
            params![table, row_key, row_json],
        )
        .map_err(sqlite_error)?;
    if changed == 0 {
        return Err(PortError::Message(format!("row not found in {table}")));
    }
    Ok(())
}

fn body_object(body: &Value) -> PortResult<BTreeMap<String, Value>> {
    value_object(body.clone()).map_err(|_| {
        PortError::Message("request body must be an object for write operations".to_string())
    })
}

fn value_object(value: Value) -> PortResult<BTreeMap<String, Value>> {
    match value {
        Value::Object(value) => Ok(value),
        _ => Err(PortError::Message(
            "stored row must be an object".to_string(),
        )),
    }
}

fn find_id(request: &RequestEnvelope) -> Option<Value> {
    request
        .path_params
        .get("id")
        .cloned()
        .or_else(|| request.query_params.get("id").cloned())
        .or_else(|| match &request.body {
            Value::Object(object) => object.get("id").cloned(),
            _ => None,
        })
}

fn value_key(value: Value) -> String {
    match value {
        Value::String(value) => value,
        Value::Integer(value) => value.to_string(),
        Value::Float(value) => value.to_string(),
        Value::Bool(value) => value.to_string(),
        other => serde_json::to_string(&value_to_json(&other)).unwrap_or_default(),
    }
}

fn value_to_json(value: &Value) -> serde_json::Value {
    match value {
        Value::Null => serde_json::Value::Null,
        Value::Bool(value) => serde_json::Value::Bool(*value),
        Value::Integer(value) => serde_json::Value::from(*value),
        Value::Float(value) => serde_json::Value::from(*value),
        Value::String(value) => serde_json::Value::String(value.clone()),
        Value::Bytes(value) => serde_json::Value::Array(
            value
                .iter()
                .map(|item| serde_json::Value::from(*item))
                .collect(),
        ),
        Value::Array(values) => {
            serde_json::Value::Array(values.iter().map(value_to_json).collect())
        }
        Value::Object(values) => serde_json::Value::Object(
            values
                .iter()
                .map(|(key, value)| (key.clone(), value_to_json(value)))
                .collect(),
        ),
    }
}

fn value_from_json(value: &serde_json::Value) -> Value {
    match value {
        serde_json::Value::Null => Value::Null,
        serde_json::Value::Bool(value) => Value::Bool(*value),
        serde_json::Value::Number(value) => value
            .as_i64()
            .map(Value::Integer)
            .or_else(|| value.as_f64().map(Value::Float))
            .unwrap_or(Value::Null),
        serde_json::Value::String(value) => Value::String(value.clone()),
        serde_json::Value::Array(values) => {
            Value::Array(values.iter().map(value_from_json).collect())
        }
        serde_json::Value::Object(values) => Value::Object(
            values
                .iter()
                .map(|(key, value)| (key.clone(), value_from_json(value)))
                .collect(),
        ),
    }
}

fn value_from_json_str(raw: &str) -> PortResult<Value> {
    let value = serde_json::from_str(raw).map_err(json_error)?;
    Ok(value_from_json(&value))
}

fn sqlite_error(error: rusqlite::Error) -> PortError {
    PortError::Message(error.to_string())
}

fn json_error(error: serde_json::Error) -> PortError {
    PortError::Message(error.to_string())
}
