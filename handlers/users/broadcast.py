import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import exceptions, executor


logging.basicConfig(level=logging.INFO)
log = logging.getLogger('broadcast')


async def send_message(message: Message, user_id: int, disable_notification: bool = False) -> bool:
    """
    Safe messages sender

    :param user_id:
    :param disable_notification:
    :return:
    """
    try:
        await message.copy_to(user_id, disable_notification=disable_notification)
    except exceptions.BotBlocked:
        log.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        log.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        log.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(message, user_id)  # Recursive call
    except exceptions.UserDeactivated:
        log.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        log.exception(f"Target [ID:{user_id}]: failed")
    else:
        log.info(f"Target [ID:{user_id}]: success")
        return True
    return False


async def broadcaster(users, message) -> int:
    """
    Simple broadcaster

    :return: Count of messages
    """
    count = 0
    try:
        for user_id in users:
            if await send_message(message, user_id):
                count += 1
            await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
    finally:
        log.info(f"{count} messages successful sent.")

    return count

