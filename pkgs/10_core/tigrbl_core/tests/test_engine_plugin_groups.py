from tigrbl_core._spec import plugins


def test_loader_accepts_canonical_and_legacy_entry_point_groups(monkeypatch) -> None:
    loaded = []

    class EntryPoint:
        def __init__(self, name, group):
            self.name = name
            self.group = group

        def load(self):
            return lambda: loaded.append((self.name, self.group))

    entries = {
        "tigrbl.engine_plugins": [EntryPoint("mysql", "canonical")],
        "tigrbl.engine": [EntryPoint("sqlite", "legacy"), EntryPoint("mysql", "legacy")],
    }
    monkeypatch.setattr(plugins, "entry_points", lambda *, group: entries[group])
    monkeypatch.setattr(plugins, "_LOADED", False)

    plugins.load_engine_plugins()

    assert loaded == [("mysql", "canonical"), ("sqlite", "legacy")]
