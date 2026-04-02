# Next Steps

## Position after the Phase 14 handoff checkpoint

The repository now has:

- a frozen current-boundary stable release bundle at `docs/conformance/releases/0.3.18/`
- a retained promotion-source dev bundle at `docs/conformance/dev/0.3.18.dev1/`
- an active next-line dev bundle scaffold at `docs/conformance/dev/0.3.19.dev1/`
- a governed next-target planning document at `docs/conformance/NEXT_TARGETS.md`
- next-target ADRs for the datatype/table program under `docs/adr/`

No in-boundary gates remain open for release `0.3.18`.

## Immediate follow-on work

### 1. Preserve release history

- keep `docs/conformance/releases/0.3.18/` frozen except for governed corrective maintenance
- keep `docs/conformance/dev/0.3.18.dev1/` as the exact promotion-source bundle for the stable release
- keep current-boundary certification wording attached only to the frozen stable release

### 2. Start governed next-target design closure

Use `docs/conformance/NEXT_TARGETS.md` as the active planning surface for:

- datatype semantic-center design
- engine lowering and bridge design
- `ColumnSpec.datatype` integration
- table portability/interoperability design
- reflection and round-trip recovery planning

### 3. Keep planning disciplined

- use ADRs and governed conformance docs before creating loose WIP notes
- keep the active line at planning/implementation wording only until real closure exists
- do not silently drift next-target work back into the frozen `0.3.18` current-target claim set
