import asyncio
from types import SimpleNamespace

import pytest

from tigrbl import (
    first_table_record,
    invoke_table_operation,
    list_table_records,
    provideTableHandler,
    read_table_record,
)


def table_with_operation(alias, target, core):
    class Widget:
        __table__ = SimpleNamespace(
            primary_key=SimpleNamespace(columns=(SimpleNamespace(name="widget_key"),))
        )
        handlers = SimpleNamespace(**{alias: SimpleNamespace(core=core)})
        ops = SimpleNamespace(
            by_alias={alias: SimpleNamespace(target=target)},
        )

    return Widget


def test_read_record_uses_bound_primary_key_and_operation_target():
    contexts = []

    async def core(ctx):
        contexts.append(ctx)
        return {"item": "found"}

    widget = table_with_operation("read", "read", core)

    result = asyncio.run(read_table_record(widget, object(), "item-1"))

    assert result == {"item": "found"}
    assert contexts[0]["target"] == "read"
    assert contexts[0]["path_params"] == {"widget_key": "item-1"}


def test_invoke_uses_custom_operation_target():
    contexts = []

    async def core(ctx):
        contexts.append(ctx)

    widget = table_with_operation("inspect", "read", core)

    asyncio.run(invoke_table_operation(widget, "inspect", db=object()))

    assert contexts[0]["op"] == "inspect"
    assert contexts[0]["target"] == "read"


def test_provided_handler_validates_payload_before_dispatch():
    called = False

    def reject(_payload):
        raise ValueError("rejected")

    async def core(_ctx):
        nonlocal called
        called = True

    widget = table_with_operation("create", "create", core)
    handler = provideTableHandler(widget, payload_validator=reject)

    with pytest.raises(ValueError, match="rejected"):
        asyncio.run(handler({"db": object(), "payload": {"name": "widget"}}))

    assert called is False


def test_list_and_first_record_pass_filters_as_operation_payload():
    contexts = []

    async def core(ctx):
        contexts.append(ctx)
        return {"items": [{"widget_key": "item-1"}]}

    widget = table_with_operation("list", "list", core)
    filters = {"widget_key": "item-1"}

    rows = asyncio.run(list_table_records(widget, object(), filters))
    first = asyncio.run(first_table_record(widget, object(), filters))

    assert rows == [{"widget_key": "item-1"}]
    assert first == {"widget_key": "item-1"}
    assert [ctx["payload"] for ctx in contexts] == [filters, filters]
