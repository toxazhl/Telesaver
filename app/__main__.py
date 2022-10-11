import asyncio
import logging.config
import os

import yaml
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.configreader import Config
from app.bot.bot import Bot
from app.client.client import Client
from app.web_server.webserver import Webserver


def setup_logging() -> None:
    with open("app/logging.yaml", "r") as stream:
        logging_config = yaml.load(stream, Loader=yaml.FullLoader)

    # Create log directories if not exists
    for handler in logging_config["handlers"].values():
        if log_filename := handler.get("filename"):
            os.makedirs(os.path.dirname(log_filename), exist_ok=True)

    logging.config.dictConfig(logging_config)


async def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting")

    config = Config()

    engine = create_async_engine(
        config.storage.postgres_dsn, future=True, echo=False
    )
    db_pool = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    bot = Bot(
        session_name=config.bot.session_name,
        api_id=config.client.api_id,
        api_hash=config.client.api_hash,
        token=config.bot.token,
        fsm_storage=config.bot.fsm_storage,
        redis_dsn=config.storage.redis_dsn,
        db_pool=db_pool,
    )

    client = Client(
        session_name=config.client.session_name,
        api_id=config.client.api_id,
        api_hash=config.client.api_hash,
        pyro_bot=bot.pyro_bot,
        db_pool=db_pool,
    )

    try:
        if config.webhook.enable:
            webserver = Webserver()
            await bot.setup_webhook(
                app=webserver.app,
                domain=config.webhook.domain,
                path=config.webhook.path.bot,
            )
            await webserver.run(
                host=config.webapp.host, port=config.webapp.port
            )

        else:
            await bot.run_polling()

        await client.run()
        logger.info("Started")
        await asyncio.Event().wait()

    finally:
        if config.webhook.enable:
            await Webserver.stop()

        await bot.stop()
        await client.stop()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
