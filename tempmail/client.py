import asyncio
from typing import Optional

import curl_cffi
from bs4 import BeautifulSoup

from .models import AccountResult, EmailResult

BASE_URL = "https://mob2.10minemail.com"


class Tempmail10:
    def __init__(self, proxy: Optional[str] = None):
        self.token: Optional[str] = None
        self.mailbox: Optional[str] = None
        self.ses = curl_cffi.AsyncSession(proxy=proxy, impersonate="chrome136")
        self.ses.headers.update({"accept": "application/json"})

    async def __aenter__(self) -> "Tempmail10":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def close(self) -> None:
        await self.ses.close()

    async def create_account(self) -> AccountResult:
        """Generate a new temporary email address."""
        try:
            resp = await self.ses.post(
                f"{BASE_URL}/mailbox",
                headers={"content-length": "0"},
                data="",
            )
            _raise_for_status(resp)
            data = resp.json()
            self.token = data["token"]
            self.mailbox = data["mailbox"]
            self.ses.headers["authorization"] = self.token
            return AccountResult(
                success=True,
                message="success create tempmail",
                email_address=self.mailbox,
            )
        except Exception as e:
            return AccountResult(success=False, message=f"error create account {e}")

    async def get_latest_message(self) -> EmailResult:
        """Fetch the most recent email in the mailbox."""
        try:
            resp = await self.ses.get(f"{BASE_URL}/messages")
            _raise_for_status(resp)
            messages = resp.json().get("messages", [])
            if not messages:
                return EmailResult(
                    success=False, message="No emails received", empty=True
                )
            message_id = messages[0]["_id"]
            resp = await self.ses.get(f"{BASE_URL}/messages/{message_id}/")
            _raise_for_status(resp)
            data = resp.json()
            html = data.get("bodyHtml") or ""
            text = BeautifulSoup(html, "html.parser").text if html else None
            return EmailResult(
                success=True,
                message="successfully retrieved the latest email",
                sender=data.get("from"),
                subject=data.get("subject"),
                html=html or None,
                text=text,
            )
        except Exception as e:
            return EmailResult(
                success=False, message=f"Unable to retrieve the latest email, error {e}"
            )

    async def wait_for_message(
        self, timeout: float = 120.0, poll_interval: float = 3.0
    ) -> EmailResult:
        """Poll the mailbox until an email arrives or timeout is reached."""
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout
        while True:
            result = await self.get_latest_message()
            if result.success:
                return result
            if not result.empty:
                return result
            if loop.time() >= deadline:
                return EmailResult(
                    success=False,
                    message=f"timeout after {timeout}s waiting for email",
                )
            await asyncio.sleep(poll_interval)


def _raise_for_status(resp) -> None:
    if resp.status_code >= 400:
        body = (resp.text or "").strip()
        detail = f": {body}" if body else ""
        raise RuntimeError(f"HTTP {resp.status_code}{detail}")
