from pyrogram import Client
from pyrogram_middleware_patch.types import OnUpdateMiddleware


class PyroBotMiddleware(OnUpdateMiddleware):
    def __init__(self, bot: Client):
        super().__init__()
        self.bot = bot

    async def __call__(self, update) -> dict:
        return {"pyro_bot": self.bot}
