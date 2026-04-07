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
        OpChannel {
            kind: protocol.to_string(),
            family: derive_family(protocol, exchange),
            exchange: exchange.to_string(),
            protocol: protocol.to_string(),
            path: path.to_string(),
            selector: Some(path.to_string()),
            framing: framing.map(|item| item.to_string()),
            subevents: derive_subevents(protocol, exchange),
        }
    }
}

pub fn derive_family(protocol: &str, exchange: &str) -> ChannelFamily {
    if protocol.starts_with("ws") {
        return ChannelFamily::Socket;
    }
    if protocol == "webtransport" {
        return ChannelFamily::Session;
    }
    if matches!(exchange, "server_stream" | "bidirectional_stream" | "event_stream") {
        return ChannelFamily::Stream;
    }
    ChannelFamily::Response
}

pub fn derive_subevents(protocol: &str, exchange: &str) -> Vec<ChannelSubevent> {
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
