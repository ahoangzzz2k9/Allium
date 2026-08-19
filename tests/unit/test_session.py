from datetime import datetime, timedelta, timezone

from src.security.session import SessionManager


def test_session_starts_authenticated():
    session = SessionManager()
    session.authenticate()
    assert session.is_authenticated()


def test_session_times_out_after_thirty_minutes():
    session = SessionManager()
    session.authenticate()
    assert session.last_activity is not None

    expired_at = session.last_activity + timedelta(minutes=30)
    assert not session.is_authenticated(expired_at)
    assert not session.is_authenticated(datetime.now(timezone.utc))
