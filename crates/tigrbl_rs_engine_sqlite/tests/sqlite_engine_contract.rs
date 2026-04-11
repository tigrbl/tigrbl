use tigrbl_rs_engine_sqlite::engine::SqliteEngine;
use tigrbl_rs_ports::engines::EnginePort;

#[test]
fn sqlite_engine_opens_session_and_transaction() {
    let engine = SqliteEngine;
    assert_eq!(engine.kind(), "sqlite");

    let session = engine.open().expect("session");
    let tx = session.begin().expect("transaction");
    tx.commit().expect("commit");
    tx.rollback().expect("rollback");
}
