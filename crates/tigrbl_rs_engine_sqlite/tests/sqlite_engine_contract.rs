use tigrbl_rs_engine_sqlite::engine::SqliteEngine;
use tigrbl_rs_ports::engines::EnginePort;
use tigrbl_rs_spec::{request::RequestEnvelope, values::Value};

use std::collections::BTreeMap;

#[test]
fn sqlite_engine_opens_session_and_transaction() {
    let engine = SqliteEngine::memory();
    assert_eq!(engine.kind(), "sqlite");

    let session = engine.open().expect("session");
    let tx = session.begin().expect("transaction");
    tx.commit().expect("commit");

    let tx = session.begin().expect("transaction");
    tx.rollback().expect("rollback");
}

#[test]
fn sqlite_engine_initializes_file_schema_when_session_opens() {
    let path = std::env::temp_dir().join(format!(
        "tigrbl-rs-engine-sqlite-schema-{}.sqlite3",
        std::process::id()
    ));
    let _ = std::fs::remove_file(&path);

    let engine = SqliteEngine::new(Some(path.to_string_lossy().into_owned()));
    let _session = engine.open().expect("session");

    let connection = rusqlite::Connection::open(&path).expect("sqlite connection");
    let exists: bool = connection
        .query_row(
            "SELECT EXISTS(
                SELECT 1 FROM sqlite_master
                WHERE type = 'table' AND name = '_tigrbl_rows'
            )",
            [],
            |row| row.get(0),
        )
        .expect("schema probe");

    assert!(exists);
    let _ = std::fs::remove_file(path);
}

#[test]
fn sqlite_engine_persists_create_rows_to_file() {
    let path = std::env::temp_dir().join(format!(
        "tigrbl-rs-engine-sqlite-{}.sqlite3",
        std::process::id()
    ));
    let _ = std::fs::remove_file(&path);

    let engine = SqliteEngine::new(Some(path.to_string_lossy().into_owned()));
    let session = engine.open().expect("session");
    let tx = session.begin().expect("transaction");

    let mut body = BTreeMap::new();
    body.insert("id".to_string(), Value::String("u1".to_string()));
    body.insert("name".to_string(), Value::String("Ada".to_string()));
    let response = tx
        .execute(
            "users",
            "users.create",
            "create",
            &RequestEnvelope {
                body: Value::Object(body.clone()),
                ..Default::default()
            },
        )
        .expect("create response");
    tx.commit().expect("commit");

    assert_eq!(response.status, 201);
    assert!(path.exists());

    let session = engine.open().expect("second session");
    let tx = session.begin().expect("second transaction");
    let response = tx
        .execute(
            "users",
            "users.read",
            "read",
            &RequestEnvelope {
                path_params: [("id".to_string(), Value::String("u1".to_string()))]
                    .into_iter()
                    .collect(),
                ..Default::default()
            },
        )
        .expect("read response");
    tx.rollback().expect("rollback");

    assert_eq!(response.status, 200);
    assert_eq!(response.body, Value::Object(body));
    let _ = std::fs::remove_file(path);
}
