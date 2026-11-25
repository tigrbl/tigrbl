# RPC invocation fallback verification plan

This plan defines the verification scope for the invocation boundary.

| Invocation outcome | Concrete router behavior |
| --- | --- |
| Handled success | Use the result, including an empty or already encoded reply. |
| Handled failure or security rejection | Propagate the failure without invoking fallback. |
| Unknown or ambiguous execution state | Stop without invoking fallback. |
| No dedicated persistence atom at plan compilation | Select the generic persistence atom before execution. It runs inside the same security and transaction phases. |

- Extend the mounted WebSocket JSON-RPC ULID test to assert a successful delete reply, a single call to the delete operation, and persisted deletion.
- Exercise already encoded success and authoritative failure in the kernel WebSocket session suite. Verify reply framing, the original request ID, existing error mapping, and one invocation per message.
- Assert the concrete router never invokes fallback after handled success, failure or rejection, or an unknown outcome. Prove the eligible case in the kernel compilation test, which selects exactly one persistence atom for either plan shape.
- Add a structural check in the concrete boundary suite that rejects fallback decisions based on WebSocket state, encoded response bytes, or protocol envelope fields.

Run these checks in the existing suites and attach their results to the SSOT claim.
