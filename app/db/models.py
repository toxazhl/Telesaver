from sqlalchemy import (
    Boolean,
    Column,
    BigInteger,
    String,
    ForeignKey,
    JSON,
    DateTime,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True)
    type = Column(String(16))
    message_id = Column(BigInteger)
    chat_id = Column(ForeignKey("chats.id"))
    user_id = Column(BigInteger)
    date = Column(DateTime(timezone=True))
    deleted = Column(Boolean, default=False)
    date_deleted = Column(DateTime(timezone=True))
    json = Column(JSON)

    chat = relationship("ChatModel", uselist=False, lazy="joined")


class ChatModel(Base):
    __tablename__ = "chats"

    id = Column(BigInteger, primary_key=True)
    type = Column(String(16))
    title = Column(String(128))
    first_name = Column(String(64))
    last_name = Column(String(64))
    username = Column(String(32))
