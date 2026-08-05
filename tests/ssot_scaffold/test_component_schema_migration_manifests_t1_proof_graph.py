from tigrbl_migrations import Migration, MigrationGraph


def _upgrade(_connection):
    return None


def test_migration_dag_orders_dependencies_deterministically():
    graph = MigrationGraph(
        (
            Migration("child-1", "tigrbl.test.child", upgrade=_upgrade),
            Migration("base-2", "tigrbl.test.base", parents=("base-1",), upgrade=_upgrade),
            Migration("base-1", "tigrbl.test.base", upgrade=_upgrade),
        )
    )
    graph.add_requirement_edge(revision="child-1", required_revision="base-2")
    assert graph.topological_order() == ("base-1", "base-2", "child-1")
