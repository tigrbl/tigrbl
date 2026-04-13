use tigrbl_rs_runtime::build_transport_trace;

#[test]
fn transport_trace_contract_covers_rest_rpc_and_stream_transports() {
    let rest = build_transport_trace("rest", true, true, true);
    let rpc = build_transport_trace("jsonrpc", true, false, true);
    let sse = build_transport_trace("sse", false, false, false);
    let ws = build_transport_trace("ws", true, true, false);
    let webtransport = build_transport_trace("webtransport", false, false, true);

    assert_eq!(rest[1].event, "route_match");
    assert!(rest.iter().any(|item| item.event == "error_map"));
    assert_eq!(rpc[1].event, "rpc_envelope_parse");
    assert_eq!(sse[sse.len() - 2].event, "post_emit");
    assert_eq!(ws[1].event, "channel_open");
    assert_eq!(webtransport[1].event, "channel_open");
    assert_eq!(webtransport[webtransport.len() - 2].event, "post_emit");
}
