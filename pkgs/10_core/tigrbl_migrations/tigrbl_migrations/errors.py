"""Fail-closed errors raised by component schema migration tooling."""


class MigrationError(RuntimeError):
    """Base class for migration contract failures."""


class ManifestError(MigrationError):
    """A component or storage manifest is malformed or incompatible."""


class GraphError(MigrationError):
    """A migration graph is incomplete, cyclic, or has invalid heads."""


class OwnershipError(MigrationError):
    """Database object ownership is missing, duplicated, or invalid."""


class LedgerError(MigrationError):
    """The persistent migration ledger is inconsistent."""


class LockError(MigrationError):
    """A migration execution lock cannot be acquired or released safely."""
