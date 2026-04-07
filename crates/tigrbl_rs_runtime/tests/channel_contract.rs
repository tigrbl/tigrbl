use tigrbl_rs_ports::{ChannelFamily, ChannelSubevent};
use tigrbl_rs_runtime::channel::{derive_family, derive_subevents, RuntimeChannelAdapter};

#[test]
fn runtime_channel_adapter_derives_socket_channels() {
    let adapter = RuntimeChannelAdapter::default();
    let channel = adapter.bind("wss", "/ws/widgets/{id}", "bidirectional_stream", Some("jsonrpc"));

    assert_eq!(channel.family, ChannelFamily::Socket);
    assert_eq!(channel.framing.as_deref(), Some("jsonrpc"));
    assert_eq!(channel.selector.as_deref(), Some("/ws/widgets/{id}"));
    assert!(channel.subevents.contains(&ChannelSubevent::Connect));
    assert!(channel.subevents.contains(&ChannelSubevent::Complete));
}

#[test]
fn runtime_channel_adapter_derives_stream_families() {
    assert_eq!(derive_family("https", "server_stream"), ChannelFamily::Stream);
    assert_eq!(
        derive_subevents("https", "event_stream"),
        vec![
            ChannelSubevent::Receive,
            ChannelSubevent::Emit,
            ChannelSubevent::Complete,
        ]
    );
}
