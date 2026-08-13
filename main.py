import asyncio

from tempmail10 import Tempmail10


async def main():
    async with Tempmail10() as tempmail:
        account = await tempmail.create_account()
        print(account)
        if not account.success:
            return
        result = await tempmail.wait_for_message(timeout=120)
        print(result)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
