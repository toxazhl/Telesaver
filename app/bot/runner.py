import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web
from sqlalchemy.orm import sessionmaker

from .handlers import setup_routers
from .middlewares.db import DbSessionMiddleware


logger = logging.getLogger(__name__)


async def setup_bot(
    token: str, fsm_storage: str, redis_dsn: str, db_pool: sessionmaker
) -> tuple[Bot, Dispatcher]:
    bot = Bot(token=token, parse_mode="HTML")

    if fsm_storage == "memory":
        dp = Dispatcher()
    else:
        dp = Dispatcher(storage=RedisStorage.from_url(redis_dsn))

    dp.message.filter(F.chat.type == "private")

    dp.update.middleware(DbSessionMiddleware(db_pool))

    # Register handlers
    router = setup_routers()
    dp.include_router(router)

    return bot, dp


async def setup_bot_webhook(
    bot: Bot, dp: Dispatcher, app: web.Application, domain: str, path: str
) -> None:
    me = await bot.get_me()
    url = f"{domain}{path}"

    logger.info(
        f'Run webhook for bot @{me.username} id={bot.id} - "{me.full_name}" '
        f'on "{url}"'
    )

    await bot.set_webhook(
        url=url,
        drop_pending_updates=True,
        allowed_updates=dp.resolve_used_update_types(),
    )
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    ).register(app, path=path)


async def run_bot(bot: Bot, dp: Dispatcher) -> None:
    await bot.delete_webhook()

    asyncio.create_task(
        dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    )


async def stop_bot(bot: Bot) -> None:
    logger.info("Stoping bot")
    await bot.session.close()
