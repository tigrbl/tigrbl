from __future__ import annotations

from tigrbl import ResponseSpec, TableRegistrySpec, TemplateSpec
from tigrbl_core._spec.response_resolver import resolve_response_spec


def test_table_registry_spec_defaults_to_empty_table_sequence() -> None:
    registry = TableRegistrySpec()

    assert registry.tables == ()


def test_table_registry_spec_preserves_declared_table_order() -> None:
    registry = TableRegistrySpec(tables=("users", "orders", "invoices"))

    assert tuple(registry.tables) == ("users", "orders", "invoices")


def test_table_registry_spec_roundtrips_table_identifiers_through_json() -> None:
    registry = TableRegistrySpec(tables=("users", "orders"))

    restored = TableRegistrySpec.from_json(registry.to_json())

    assert restored == registry
    assert restored.tables == ("users", "orders")


def test_template_spec_defaults_to_declarative_template_metadata() -> None:
    template = TemplateSpec(name="index.html")

    assert template.name == "index.html"
    assert template.search_paths == []
    assert template.package is None
    assert template.auto_reload is None
    assert template.filters == {}
    assert template.globals == {}


def test_template_spec_roundtrips_template_runtime_metadata() -> None:
    template = TemplateSpec(
        name="dashboard.html",
        search_paths=["templates"],
        package="admin_ui",
        auto_reload=True,
        filters={"date": "format_date"},
        globals={"section": "admin"},
    )

    restored = TemplateSpec.from_json(template.to_json())

    assert restored == template
    assert restored.filters == {"date": "format_date"}
    assert restored.globals == {"section": "admin"}


def test_response_spec_embeds_template_spec_contract() -> None:
    response = ResponseSpec(
        kind="html",
        status_code=200,
        media_type="text/html",
        template=TemplateSpec(name="users/list.html"),
    )

    restored = ResponseSpec.from_json(response.to_json())

    assert restored == response
    assert restored.template is not None
    assert restored.template.name == "users/list.html"


def test_template_spec_merge_combines_paths_filters_and_globals() -> None:
    base = ResponseSpec(
        kind="html",
        template=TemplateSpec(
            name="base.html",
            search_paths=["templates"],
            package="inventory_app",
            auto_reload=False,
            filters={"date": "format_date"},
            globals={"app_name": "Inventory"},
        ),
    )
    override = ResponseSpec(
        template=TemplateSpec(
            name="users.html",
            search_paths=["tenant_templates", "templates"],
            auto_reload=True,
            filters={"money": "format_money"},
            globals={"section": "users"},
        )
    )

    resolved = resolve_response_spec(base, override)

    assert resolved is not None
    assert resolved.template is not None
    assert resolved.template.name == "users.html"
    assert resolved.template.search_paths == ["templates", "tenant_templates"]
    assert resolved.template.package == "inventory_app"
    assert resolved.template.auto_reload is True
    assert resolved.template.filters == {
        "date": "format_date",
        "money": "format_money",
    }
    assert resolved.template.globals == {
        "app_name": "Inventory",
        "section": "users",
    }
