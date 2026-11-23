# Transport Trace Lab

Run one Tigrbl application behind Tigrcorn and drill into live identity and
lifecycle records from a real four-transport scenario. The lab uses a temporary
SQLite database, a generated QUIC certificate, and a process-local subscription
broker. Both listeners bind only to `127.0.0.1`.

## Run

Use a Python 3.13 development environment with Tigrbl and Tigrcorn dependencies
installed, including `httpx`, `websockets>=15`, and the SQLite provider. The runner
loads the selected source checkouts directly so the identity features are available
before a package release. It imports Tigrcorn's QUIC test client from that checkout.
The verified source revisions were Tigrbl `4c845df`, Tigrcorn `264c911`, and
tigr-asgi-contract `1902171`, or use newer checkouts that include those commits.

From the Tigrbl repository root, run the following. Replace the source paths
with your checkouts. The flags default to the current Tigrbl repository and its
sibling Tigrcorn and contract repositories.

```sh
python pkgs/96_examples/transport_surface_matrix_demo/trace_lab/run.py
```

Open the printed loopback URL and select **Run all transports**. The dashboard
refreshes while events arrive. Select a dimension and an ID, then follow a
related ID or open a timeline event to inspect all of its captured fields.
**Clear selection** returns to the complete timeline.

- **REST** creates a note in SQLite through the bound `POST /notes` operation.
- **JSON-RPC over HTTP** reads the same note with `Note.read` at `/rpc`. Compare the
  two request correlations and drill from their invocations into the engine
  transactions.
- **WebSocket** uses two clients at `/ws/activity`. One calls
  `Activity.subscribe` with a v2 acknowledgement. The other calls
  `Activity.publish`, and the subscriber receives the notification. Follow the
  delivery to the destination attachment or the publisher's invocation.
- **WebTransport** opens two sessions on one HTTP/3 QUIC connection across a UDP
  rebind. It sends a length-prefixed `Trace.echo` JSON-RPC request on a
  bidirectional stream and sends datagrams. The probe's second session also
  exercises rejection of a malformed stream record. Follow the shared
  connection to two session correlations and their stream correlations.

The button runs the clients on the local server so the browser needs no QUIC
certificate installation. `GET /demo/trace` returns the latest 750 identity
records and the Tigrbl rollup. The dashboard stores metadata for drillback.
The broker and timeline are process-local. Stopping the server clears the
timeline and deletes the temporary database. Subscription reconnect and
distributed quota lease transfer are covered by separate framework tests.

## Verify

Add `--port 0 --smoke` to the command to run the scenario against ephemeral
loopback ports and exit. The smoke checks the REST write and RPC read, the
actual WebSocket delivery, the framed WebTransport reply, the QUIC session
grouping, and the transaction-to-invocation links.

The example captures packed execution snapshots and reads provider lifecycle
records for the request-owned SQLite session when the fast runner leaves those
events out of the snapshot. For the declared WebSocket route, the demo adapter
unwraps encoded operation responses before the existing JSON-RPC dispatcher
frames them.
