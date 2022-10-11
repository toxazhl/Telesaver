from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from .models import ChatModel, MessageModel


async def commit(session: AsyncSession, *instances) -> None:
    if instances:
        session.add_all(instances)
    await session.commit()


async def insert_message(
    session: AsyncSession,
    message_id: int,
    type: str,
    chat_id: int,
    user_id: None | int,
    date: datetime,
    json: dict,
) -> MessageModel:
    message = MessageModel(
        message_id=message_id,
        type=type,
        chat_id=chat_id,
        user_id=user_id,
        date=date,
        json=json,
    )
    session.add(message)

    return message


async def get_message(
    session: AsyncSession, message_id: int, chat_id: None | int
) -> MessageModel:
    stmt = (
        select(MessageModel)
        .where(MessageModel.message_id == message_id)
        .join(ChatModel)
        .order_by(MessageModel.id)
    )

    if chat_id:
        stmt = stmt.where(MessageModel.chat_id == chat_id)

    else:
        stmt = stmt.where(ChatModel.type == "PRIVATE")

    return await session.scalar(stmt)


async def insert_chat(
    session: AsyncSession,
    id: int,
    type: str,
    title: None | str,
    username: None | str,
    first_name: None | str,
    last_name: None | str,
) -> None:
    stmt = (
        insert(ChatModel)
        .values(
            id=id,
            type=type,
            title=title,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        .on_conflict_do_update(
            index_elements=["id"],
            set_=dict(
                title=title,
                username=username,
                first_name=first_name,
                last_name=last_name,
            ),
        )
    )
    await session.execute(stmt)
