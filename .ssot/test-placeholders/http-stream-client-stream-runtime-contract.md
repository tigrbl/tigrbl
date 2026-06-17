# HTTP Stream Client Stream Runtime Contract

Planned runtime coverage for HTTP request-body streaming.

The eventual executable test must prove request body chunks project as
client_stream events for declared HTTP stream request bindings, preserve chunk
order, preserve end-of-body state, and avoid collapsing the stream into one
opaque unary request body.
