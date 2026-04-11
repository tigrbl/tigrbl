use tigrbl_rs_engine_inmemory::engine::InmemoryEngine;
use tigrbl_rs_ports::engines::EnginePort;

#[test]
fn inmemory_engine_opens_session_and_transaction() {
    let engine = InmemoryEngine;
    assert_eq!(engine.kind(), "inmemory");

    let session = engine.open().expect("session");
    let tx = session.begin().expect("transaction");
    tx.commit().expect("commit");
    tx.rollback().expect("rollback");
}
