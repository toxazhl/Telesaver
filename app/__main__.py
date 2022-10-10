import asyncio
import logging.config
import os

import yaml
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from pyrogram.methods.utilities.idle import idle

from app.configreader import Config
from app.bot.runner import run_bot, setup_bot, setup_bot_webhook, stop_bot
from app.client.runner import run_client, setup_client, stop_client
from app.web_server.runner import run_server, setup_server, stop_server


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

    bot, dp = await setup_bot(
        token=config.bot.token,
        fsm_storage=config.bot.fsm_storage,
        redis_dsn=config.storage.redis_dsn,
        db_pool=db_pool,
    )

    client = await setup_client(
        session_name=config.client.session_name,
        api_id=config.client.api_id,
        api_hash=config.client.api_hash,
        db_pool=db_pool,
    )

    if config.webhook.enable:
        app, site = setup_server(
            host=config.webapp.host, port=config.webapp.port
        )
        await setup_bot_webhook(
            bot=bot,
            dp=dp,
            app=app,
            domain=config.webhook.domain,
            path=config.webhook.path.bot,
        )
        await run_server(site=site)

    else:
        await run_bot(bot=bot, dp=dp)

    await run_client(client=client)

    logger.info("Started")
    await idle()

    await stop_bot(bot=bot)
    await stop_client(client=client)

    if config.webhook.enable:
        await stop_server(site=site)


if __name__ == "__main__":
    asyncio.run(main())
