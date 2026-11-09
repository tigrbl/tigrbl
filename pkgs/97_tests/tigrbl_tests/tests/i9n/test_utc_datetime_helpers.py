from datetime import datetime, timedelta, timezone

from tigrbl.orm import mixins
from tigrbl.types import tzutcnow, tzutcnow_plus_day


def test_utc_helpers_are_available_from_public_and_legacy_imports():
    assert mixins.tzutcnow is tzutcnow
    assert mixins.tzutcnow_plus_day is tzutcnow_plus_day

    before = datetime.now(timezone.utc)
    now = tzutcnow()
    tomorrow = tzutcnow_plus_day()
    after = datetime.now(timezone.utc)

    assert now.utcoffset() == timedelta(0)
    assert tomorrow.utcoffset() == timedelta(0)
    assert before <= now <= after
    assert before + timedelta(days=1) <= tomorrow <= after + timedelta(days=1)
