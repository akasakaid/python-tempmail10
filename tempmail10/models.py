from dataclasses import dataclass
from typing import Optional


@dataclass
class AccountResult:
    success: bool
    message: str
    email_address: Optional[str] = None


@dataclass
class EmailResult:
    success: bool
    message: str
    sender: Optional[str] = None
    subject: Optional[str] = None
    html: Optional[str] = None
    text: Optional[str] = None
    empty: bool = False
