# Target Selection Policy

A target belongs in the current certification boundary only when all of the following are true:

1. it is owned by the framework rather than delegated to the server/runtime
2. it is exposed as a public or operator-relevant surface
3. it can be documented precisely
4. it can be tested reproducibly
5. it can be evidenced in the claim registry and gate model

A target should stay deferred or out-of-boundary when:

- ownership is shared with or dominated by the server/runtime
- the public contract is not yet stable
- tests or evidence cannot yet support a certifiable claim


## UI-only surface rule

If a spec emission surface exists but an interactive UI does not, the current boundary may keep the emitted spec and explicitly de-scope the UI row instead of overstating closure.
