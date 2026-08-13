# python-tempmail10

Async temporary email client for [10minemail](https://10minemail.com), built on
[`curl_cffi`](https://github.com/lexiforest/curl_cffi) with browser impersonation.

Create a disposable mailbox, then poll for incoming messages — useful for
automated sign-up flows, OTP retrieval, and testing email delivery.

## Features

- Fully async API (`asyncio`).
- Browser TLS impersonation via `curl_cffi` (Chrome).
- Optional proxy support.
- Async context manager for automatic session cleanup.
- Typed result objects (`AccountResult`, `EmailResult`).
- HTML emails parsed to plain text out of the box.

## Requirements

- Python >= 3.9
- [`curl_cffi`](https://pypi.org/project/curl-cffi/)
- [`beautifulsoup4`](https://pypi.org/project/beautifulsoup4/)

## Installation

```bash
pip install python-tempmail10
```

From source:

```bash
git clone https://github.com/yourname/python-tempmail10.git
cd python-tempmail10
pip install -e .
```

## Quick start

```python
import asyncio

from tempmail import Tempmail10


async def main():
    async with Tempmail10() as tempmail:
        account = await tempmail.create_account()
        print(account)
        if not account.success:
            return

        print("Your address:", account.email_address)

        # Block until an email arrives (or timeout).
        result = await tempmail.wait_for_message(timeout=120)
        if result.success:
            print("From:   ", result.sender)
            print("Subject:", result.subject)
            print("Text:   ", result.text)
        else:
            print("No email:", result.message)


if __name__ == "__main__":
    asyncio.run(main())
```

## Usage

### Creating a client

```python
from tempmail import Tempmail10

# Default
tempmail = Tempmail10()

# With a proxy
tempmail = Tempmail10(proxy="http://user:pass@host:port")
```

`Tempmail10` is an async context manager. Prefer `async with` so the underlying
HTTP session is always closed:

```python
async with Tempmail10() as tempmail:
    ...
```

If you manage the lifecycle manually, call `await tempmail.close()` when done.

### Creating a mailbox

```python
account = await tempmail.create_account()
# AccountResult(success=True, message='success create tempmail',
#               email_address='abc123@somedomain.com')
```

### Fetching the latest message

```python
result = await tempmail.get_latest_message()
if result.success:
    print(result.subject, result.sender)
elif result.empty:
    print("Mailbox is empty (no messages yet)")
else:
    print("Error:", result.message)
```

### Waiting for a message

`wait_for_message` polls until a message arrives, a fatal error occurs, or the
timeout is reached. Empty mailboxes are retried; fatal errors (auth/network)
return immediately.

```python
result = await tempmail.wait_for_message(timeout=120, poll_interval=3)
```

## API reference

### `Tempmail10(proxy: Optional[str] = None)`

| Method | Returns | Description |
| --- | --- | --- |
| `await create_account()` | `AccountResult` | Generate a new temporary email address. |
| `await get_latest_message()` | `EmailResult` | Fetch the most recent email in the mailbox. |
| `await wait_for_message(timeout=120.0, poll_interval=3.0)` | `EmailResult` | Poll until an email arrives or timeout. |
| `await close()` | `None` | Close the underlying HTTP session. |

### `AccountResult`

| Field | Type | Description |
| --- | --- | --- |
| `success` | `bool` | Whether the account was created. |
| `message` | `str` | Human-readable status message. |
| `email_address` | `Optional[str]` | The generated address (on success). |

### `EmailResult`

| Field | Type | Description |
| --- | --- | --- |
| `success` | `bool` | Whether an email was retrieved. |
| `message` | `str` | Human-readable status message. |
| `sender` | `Optional[str]` | Sender address. |
| `subject` | `Optional[str]` | Email subject. |
| `html` | `Optional[str]` | Raw HTML body. |
| `text` | `Optional[str]` | Plain-text body (parsed from HTML). |
| `empty` | `bool` | `True` when the mailbox has no messages yet. |

## Error handling

All client methods return result objects instead of raising on network/API
failures. Inspect `success` (and `empty` for `EmailResult`) rather than wrapping
calls in `try/except`:

```python
result = await tempmail.get_latest_message()
if not result.success and not result.empty:
    # Genuine error (auth, network, server): message contains details.
    print(result.message)
```

## Disclaimer

This library interacts with a third-party service that is not affiliated with
this project. Use it responsibly and in accordance with the service's terms.
Intended for testing and automation, not abuse.

## License

MIT
