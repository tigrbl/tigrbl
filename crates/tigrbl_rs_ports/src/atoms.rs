pub trait AtomPort: Send + Sync {
    fn atom_name(&self) -> &str;
}
