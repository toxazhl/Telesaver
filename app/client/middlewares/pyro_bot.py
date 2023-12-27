from pyrogram import Client
from pyrogram_patch.middlewares import PatchHelper
from pyrogram_patch.middlewares.middleware_types import OnUpdateMiddleware


class PyroBotMiddleware(OnUpdateMiddleware):
    def __init__(self, bot: Client):
        super().__init__()
        self.bot = bot

    async def __call__(self, update, client, patch_helper: PatchHelper):
        patch_helper.data["pyro_bot"] = self.bot
