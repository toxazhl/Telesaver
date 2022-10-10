import logging

from aiohttp import web


logger = logging.getLogger(__name__)


async def setup_server(
    host: str, port: int
) -> tuple[web.Application, web.TCPSite]:
    app = web.Application()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=host, port=port)
    return app, site


async def run_server(site: web.TCPSite) -> None:
    logger.info(f"Running web server on {site._host}:{site._host}")
    await site.start()


async def stop_server(site: web.TCPSite) -> None:
    logger.info("Stoping server")
    await site.stop()
