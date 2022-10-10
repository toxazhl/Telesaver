import logging

from pyrogram import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)


async def new_message(
    client: Client, message: Message, session: AsyncSession
) -> None:
    logger.info(f"New message {message.id} in chat {message.chat.id}")
    logger.debug(message)


def setup_routers(client: Client) -> None:
    client.add_handler(MessageHandler(new_message))
