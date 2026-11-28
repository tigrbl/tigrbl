from tigrbl_trace_transport import TraceExporter

exporter = TraceExporter("http://127.0.0.1:8766", "example-token", "notes", "local")

# Pass trace_sink=exporter.capture when constructing the Tigrbl app.
# Call exporter.start() at worker startup and await exporter.close() at shutdown.
assert callable(exporter.capture)
