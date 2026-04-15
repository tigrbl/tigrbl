# Certification Truth Model

# Certification Truth Model

## Purpose

Define the repository-level certification control model that separates release-grade facts from planning facts.

## States

- `current`: frozen current-boundary claim or control
- `target`: planned next-target feature or claim
- `blocked`: known blocker that prevents promotion or certification
- `evidenced`: claim or gate backed by evidence artifacts

## Required fields

### Public claim

- `id`
- `title`
- `owner`
- `public`
- `certified_boundary`

### Next-target feature

- `id`
- `name`
- `owner`
- `package`
- `crate`
- `test_class`
- `claim_target`
- `phase`

### Risk

- `id`
- `title`
- `mitigation`
- `mitigation_owner`

### Issue

- `id`
- `title`
- `state`
- `phase_link` or `waiver`

## Authority rule

If a narrative document conflicts with `certification/`, the `certification/` tree wins.
