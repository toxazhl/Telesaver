import logging
from datetime import datetime

from pyrogram import Client
from pyrogram.filters import Filter
from pyrogram.handlers import DeletedMessagesHandler
from pyrogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.client.utils import copy_message, parse_object
from app.db import queries

logger = logging.getLogger(__name__)


async def delete_message(
    client: Client,
    messages: list[Message],
    pyro_bot: Client,
    session: AsyncSession,
) -> None:
    for message in messages:
        logger.info(f"Delete message {repr(message)}")
        message = await queries.get_message(
            session=session,
            message_id=message.id,
            chat_id=message.chat.id if message.chat else None,
        )
        if message is None:
            logger.warn(f"Message {repr(message)} not found")

        message.deleted = True
        message.date_deleted = datetime.now()
        await queries.commit(session, message)

        message: Message = parse_object.parse(obj=message.json, client=pyro_bot)
        bot_message = await copy_message.copy(pyro_bot, message, client.me.id)
        user = message.from_user
        chat = message.chat

        if chat.username:
            chat = f"@{chat.username}"
        else:
            chat = f"<code>{chat.title}</code> [<code>{chat.id}</code>]"

        await bot_message.reply(
            f"Message[<code>{message.id}</code>] from {user.mention}"
            f"[<code>{user.id}</code>] in {chat}",
            quote=True,
        )


def setup_routers(client: Client, filters: None | Filter = None) -> None:
    client.add_handler(DeletedMessagesHandler(delete_message, filters))
