from tigrbl.factories.engine import engine_spec, mysql, mysql_cfg


def test_mysql_aliases_build_engine_config() -> None:
    config = mysql(user="portwyrm", pwd="secret", host="db", name="control")
    assert config == mysql_cfg(user="portwyrm", pwd="secret", host="db", name="control")
    spec = engine_spec(config)
    assert spec.kind == "mysql"
    assert spec.mapping["db"] == "control"
