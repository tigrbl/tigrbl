#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct TransportTraceEvent {
    pub event: String,
    pub transport: String,
}

pub fn build_transport_trace(
    transport: &str,
    include_hook: bool,
    include_error: bool,
    include_docs: bool,
) -> Vec<TransportTraceEvent> {
    let transport = transport.to_lowercase();
    let mut events = vec![TransportTraceEvent {
        event: "request_entry".to_string(),
        transport: transport.clone(),
    }];
    let route_event = match transport.as_str() {
        "rest" => "route_match",
        "jsonrpc" => "rpc_envelope_parse",
        "sse" => "stream_open",
        "ws" | "wss" | "webtransport" => "channel_open",
        _ => "route_match",
    };
    events.push(TransportTraceEvent {
        event: route_event.to_string(),
        transport: transport.clone(),
    });
    if include_hook {
        events.push(TransportTraceEvent {
            event: "callback_fence_enter".to_string(),
            transport: transport.clone(),
        });
        events.push(TransportTraceEvent {
            event: "callback_fence_exit".to_string(),
            transport: transport.clone(),
        });
    }
    events.push(TransportTraceEvent {
        event: "handler_dispatch".to_string(),
        transport: transport.clone(),
    });
    if include_error {
        events.push(TransportTraceEvent {
            event: "error_map".to_string(),
            transport: transport.clone(),
        });
    }
    if include_docs {
        events.push(TransportTraceEvent {
            event: "docs_emit".to_string(),
            transport: transport.clone(),
        });
    }
    if matches!(transport.as_str(), "sse" | "ws" | "wss" | "webtransport") {
        events.push(TransportTraceEvent {
            event: "post_emit".to_string(),
            transport: transport.clone(),
        });
    }
    events.push(TransportTraceEvent {
        event: "response_exit".to_string(),
        transport,
    });
    events
}
