# H3 Non-WebTransport Stream Taxonomy Contract

Planned unit coverage for plain HTTP/3 stream taxonomy.

The eventual executable test must distinguish request streams, push streams,
control streams, QPACK streams, and extension streams. It must reject treating
control or QPACK streams as app-level payload carriers and must keep
WebTransport semantics out of plain h3 rows.
