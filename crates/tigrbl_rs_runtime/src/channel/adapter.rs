use tigrbl_rs_ports::{ChannelFamily, ChannelSubevent, OpChannel};

#[derive(Debug, Clone, Default)]
pub struct RuntimeChannelAdapter;

impl RuntimeChannelAdapter {
    pub fn bind(
        &self,
        protocol: &str,
        path: &str,
        exchange: &str,
        framing: Option<&str>,
    ) -> OpChannel {
        let normalized_exchange = normalize_exchange(exchange);
        OpChannel {
            kind: derive_kind(protocol, normalized_exchange).to_string(),
            family: derive_family(protocol, normalized_exchange),
            exchange: normalized_exchange.to_string(),
            protocol: protocol.to_string(),
            path: path.to_string(),
            selector: Some(path.to_string()),
            framing: framing.map(|item| item.to_string()),
            subevents: derive_subevents(protocol, normalized_exchange),
        }
    }
}

pub fn normalize_exchange(exchange: &str) -> &str {
    if exchange == "bidirectional" {
        "bidirectional_stream"
    } else {
        exchange
    }
}

pub fn derive_kind(protocol: &str, exchange: &str) -> &'static str {
    let exchange = normalize_exchange(exchange);
    if protocol.starts_with("ws") {
        return "websocket";
    }
    if protocol == "webtransport" {
        return "webtransport";
    }
    if exchange == "event_stream" {
        return "sse";
    }
    if exchange == "server_stream" {
        return "stream";
    }
    "http"
}

pub fn derive_family(protocol: &str, exchange: &str) -> ChannelFamily {
    let exchange = normalize_exchange(exchange);
    if protocol.starts_with("ws") {
        return ChannelFamily::Socket;
    }
    if protocol == "webtransport" {
        return ChannelFamily::Session;
    }
    if matches!(exchange, "server_stream" | "bidirectional_stream" | "event_stream") {
        return ChannelFamily::Stream;
    }
    if exchange == "fire_and_forget" {
        ChannelFamily::Request
    } else {
        ChannelFamily::Response
    }
}

pub fn derive_subevents(protocol: &str, exchange: &str) -> Vec<ChannelSubevent> {
    let exchange = normalize_exchange(exchange);
    if protocol.starts_with("ws") || protocol == "webtransport" {
        return vec![
            ChannelSubevent::Connect,
            ChannelSubevent::Receive,
            ChannelSubevent::Emit,
            ChannelSubevent::Complete,
            ChannelSubevent::Disconnect,
        ];
    }
    if matches!(exchange, "server_stream" | "bidirectional_stream" | "event_stream") {
        return vec![
            ChannelSubevent::Receive,
            ChannelSubevent::Emit,
            ChannelSubevent::Complete,
        ];
    }
    vec![
        ChannelSubevent::Receive,
        ChannelSubevent::Emit,
        ChannelSubevent::Complete,
    ]
}
