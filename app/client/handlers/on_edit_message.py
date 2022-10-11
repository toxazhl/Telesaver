import logging
import json

from pyrogram import Client
from pyrogram.filters import Filter
from pyrogram.handlers import EditedMessageHandler
from pyrogram.types import Message, Object
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import queries


logger = logging.getLogger(__name__)


async def edit_message(
    client: Client, message: Message, session: AsyncSession
) -> None:
    logger.info(f"Edit message {message.id} in chat {message.chat.id}")

    chat = message.chat

    await queries.insert_chat(
        session=session,
        id=chat.id,
        type=chat.type.name,
        title=chat.title,
        username=chat.username,
        first_name=chat.first_name,
        last_name=chat.last_name,
    )
    await queries.insert_message(
        session=session,
        message_id=message.id,
        type="edit",
        chat_id=message.chat.id,
        user_id=message.from_user.id if message.from_user else None,
        date=message.date,
        json=json.loads(
            json.dumps(message, default=Object.default, ensure_ascii=False)
        ),
    )
    await session.commit()


def setup_routers(client: Client, filters: None | Filter = None) -> None:
    client.add_handler(EditedMessageHandler(edit_message, filters))
