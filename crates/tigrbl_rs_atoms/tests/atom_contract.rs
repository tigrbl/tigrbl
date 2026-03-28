use tigrbl_rs_atoms::{labels::phase_label, phases::AtomPhase, AtomMetadata, AtomRegistry};

#[test]
fn atom_phases_have_stable_string_reprs() {
    let labels = AtomPhase::all()
        .iter()
        .map(|phase| phase.as_str())
        .collect::<Vec<_>>();
    assert_eq!(labels.first().copied(), Some("dep"));
    assert_eq!(labels.last().copied(), Some("sys"));
    assert!(labels.contains(&"ingress"));
    assert!(labels.contains(&"error"));
}

#[test]
fn atom_registry_try_register_rejects_duplicates() {
    let mut registry = AtomRegistry::default();
    let meta = AtomMetadata {
        name: "handler.create".to_string(),
        phase: AtomPhase::Sys,
    };

    registry.try_register(meta.clone()).unwrap();
    let err = registry.try_register(meta).unwrap_err();
    assert_eq!(err.name, "handler.create");
    assert_eq!(registry.len(), 1);
}

#[test]
fn phase_labels_include_phase_prefix() {
    assert_eq!(phase_label(AtomPhase::Ingress, "decode"), "ingress::decode");
}
