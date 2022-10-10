import logging

from pyrogram import Client
from pyrogram_middleware_patch import patch
from sqlalchemy.orm import sessionmaker

from .middlewares.db import DbSessionMiddleware
from .handlers import on_message


logger = logging.getLogger(__name__)


async def setup_client(
    session_name: str, api_id: int | str, api_hash: str, db_pool: sessionmaker
) -> Client:
    client = Client(session_name, api_id, api_hash)
    patch_manager = patch(client)
    patch_manager.include_middleware(DbSessionMiddleware(db_pool))

    on_message.setup_routers(client)

    return client


async def run_client(client: Client) -> None:
    await client.start()


async def stop_client(client: Client) -> None:
    logger.info("Stoping client")
    await client.stop()
