"""Single-session timeout management for Allium.

Task 1.1 provides the concrete session lifecycle primitive. Authentication and
permission enforcement are implemented in Task 1.12; this class does not grant
permissions and does not persist credentials.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone


@dataclass
class SessionManager:
    """Manage one authenticated session with a 30-minute inactivity timeout."""

    timeout_minutes: int = 30
    _authenticated: bool = field(default=False, init=False)
    _last_activity: datetime | None = field(default=None, init=False)

    def authenticate(self) -> None:
        """Start an authenticated session."""
        self._authenticated = True
        self._last_activity = datetime.now(timezone.utc)

    def touch(self) -> None:
        """Record user activity for the active session."""
        if self._authenticated:
            self._last_activity = datetime.now(timezone.utc)

    def is_authenticated(self, now: datetime | None = None) -> bool:
        """Return whether the session is active and has not timed out."""
        if not self._authenticated or self._last_activity is None:
            return False

        current = now or datetime.now(timezone.utc)
        if current - self._last_activity >= timedelta(minutes=self.timeout_minutes):
            self.logout()
            return False
        return True

    def logout(self) -> None:
        """End the current session."""
        self._authenticated = False
        self._last_activity = None

    @property
    def last_activity(self) -> datetime | None:
        """Return the last activity timestamp for diagnostics/tests."""
        return self._last_activity
