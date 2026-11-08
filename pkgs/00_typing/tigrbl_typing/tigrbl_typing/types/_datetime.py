from datetime import datetime, timedelta, timezone


def tzutcnow() -> datetime:
    """Return the current time as a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def tzutcnow_plus_day() -> datetime:
    """Return a timezone-aware UTC datetime one day in the future."""
    return tzutcnow() + timedelta(days=1)
