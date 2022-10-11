from aiohttp import web


class Webserver:
    def __int__(self) -> None:
        self.site = None
        self.app = web.Application()
        self.runner = web.AppRunner(self.app)

    async def run(self, host: str, port: int) -> None:
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, host=host, port=port)
        await self.site.start()

    async def stop(self) -> None:
        if self.site:
            await self.site.stop()
