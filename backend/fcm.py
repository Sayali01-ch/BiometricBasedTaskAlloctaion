import os
from typing import Any


class FcmClient:
    """
    Thin wrapper around firebase-admin.
    - If not configured, send() becomes a no-op and returns {"sent": False, "reason": "..."}.
    """

    def __init__(self) -> None:
        self._enabled = False
        self._init_error: str | None = None
        self._messaging = None

        sa_path = os.getenv("FCM_SERVICE_ACCOUNT_JSON", "credentials/firebase-credentials.json")
        if not os.path.exists(sa_path):
            self._init_error = f"FCM service account not found: {sa_path}"
            return

        try:
            import firebase_admin
            from firebase_admin import credentials, messaging

            if not firebase_admin._apps:
                cred = credentials.Certificate(sa_path)
                firebase_admin.initialize_app(cred)

            self._messaging = messaging
            self._enabled = True
        except Exception as e:
            self._init_error = f"FCM init failed: {e}"

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def init_error(self) -> str | None:
        return self._init_error

    def send(self, *, token: str, title: str, body: str, data: dict[str, str] | None = None) -> dict[str, Any]:
        if not self._enabled or self._messaging is None:
            return {"sent": False, "reason": self._init_error or "not enabled"}

        msg = self._messaging.Message(
            token=token,
            notification=self._messaging.Notification(title=title, body=body),
            data=data or {},
        )
        message_id = self._messaging.send(msg)
        return {"sent": True, "message_id": message_id}

