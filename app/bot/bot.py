import asyncio

import aiogram
from pyrogram.client import Client
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web
from sqlalchemy.orm import sessionmaker

from .handlers import setup_routers
from .middlewares.db import DbSessionMiddleware


class Bot:
    def __init__(
        self,
        session_name: str,
        api_id: int | str,
        api_hash: str,
        token: str,
        fsm_storage: str,
        redis_dsn: str,
        db_pool: sessionmaker,
    ) -> None:
        self.pyro_bot = Client(
            name=session_name,
            api_id=api_id,
            api_hash=api_hash,
            bot_token=token,
            no_updates=True,
        )
        self.bot = aiogram.Bot(token=token, parse_mode="HTML")

        if fsm_storage == "memory":
            self.dp = aiogram.Dispatcher(pyro_bot=self.pyro_bot)
        else:
            self.dp = aiogram.Dispatcher(
                storage=RedisStorage.from_url(redis_dsn)
            )

        self.dp.message.filter(aiogram.F.chat.type == "private")
        self.dp.update.middleware(DbSessionMiddleware(db_pool))

        router = setup_routers()
        self.dp.include_router(router)

    async def setup_webhook(
        self, app: web.Application, domain: str, path: str
    ) -> None:
        await self.pyro_bot.start()
        await self.bot.set_webhook(
            url=f"{domain}{path}",
            drop_pending_updates=True,
            allowed_updates=self.dp.resolve_used_update_types(),
        )

        SimpleRequestHandler(
            dispatcher=self.dp,
            bot=self.bot,
        ).register(app, path=path)

    async def run_polling(self) -> None:
        await self.pyro_bot.start()

        await self.bot.delete_webhook()
        asyncio.create_task(
            self.dp.start_polling(
                self.bot, allowed_updates=self.dp.resolve_used_update_types()
            )
        )

    async def stop(self) -> None:
        await self.bot.session.close()

        try:
            await self.pyro_bot.stop()
        except ConnectionError:
            pass
