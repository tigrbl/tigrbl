from __future__ import annotations

import pytest

from tigrbl import TableBase
from tigrbl_core._spec import AppSpec, TableSpec
import tigrbl_kernel as runtime_kernel
from tigrbl.schema import builder as v3_builder


def mro_collect_app_spec(app: type):
    return AppSpec.collect(app)


def mro_collect_table_spec(model: type):
    return TableSpec.collect(model)


def _reset_tigrbl_state() -> None:
    TableBase.metadata.clear()
    v3_builder._SchemaCache.clear()
    runtime_kernel._default_kernel = runtime_kernel.Kernel()


@pytest.fixture(autouse=True)
def _reset_state():
    _reset_tigrbl_state()
    yield
    _reset_tigrbl_state()
