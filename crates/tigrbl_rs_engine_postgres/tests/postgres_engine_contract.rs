use tigrbl_rs_engine_postgres::engine::PostgresEngine;
use tigrbl_rs_ports::engines::EnginePort;

#[test]
fn postgres_engine_opens_session_and_transaction() {
    let engine = PostgresEngine;
    assert_eq!(engine.kind(), "postgres");

    let session = engine.open().expect("session");
    let tx = session.begin().expect("transaction");
    tx.commit().expect("commit");
    tx.rollback().expect("rollback");
}
