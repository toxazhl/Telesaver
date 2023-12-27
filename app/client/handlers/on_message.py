import json
import logging

from pyrogram import Client
from pyrogram.filters import Filter
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message, Object
from sqlalchemy.ext.asyncio import AsyncSession

from app.client.utils import save_media
from app.db import queries

logger = logging.getLogger(__name__)


async def new_message(client: Client, message: Message, session: AsyncSession) -> None:
    if message.chat.type == "private":
        logger.info(f"New message {message.id}")
        await queries.insert_chat(
            session=session,
            id=message.chat.id,
            type=message.chat.type.name,
            title=message.chat.title,
            username=message.chat.username,
            first_name=message.chat.first_name,
            last_name=message.chat.last_name,
        )
        await queries.insert_message(
            session=session,
            message_id=message.id,
            type="new",
            chat_id=message.chat.id,
            user_id=message.from_user.id if message.from_user else None,
            date=message.date,
            json=json.loads(
                json.dumps(message, default=Object.default, ensure_ascii=False)
            ),
        )
        await session.commit()
        await save_media.save(client, message)


def setup_routers(client: Client, filters: None | Filter = None) -> None:
    client.add_handler(MessageHandler(new_message, filters))
