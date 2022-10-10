from sqlalchemy import Column, BigInteger, column

from app.db.base import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True)
    message_id = Column(BigInteger)
    chat_id = column(BigInteger)
