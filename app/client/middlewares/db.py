from pyrogram_patch.middlewares import PatchHelper
from pyrogram_patch.middlewares.middleware_types import OnUpdateMiddleware
from sqlalchemy.orm import sessionmaker


class DbSessionMiddleware(OnUpdateMiddleware):
    def __init__(self, session_pool: sessionmaker):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(self, update, client, patch_helper: PatchHelper):
        async with self.session_pool() as session:
            patch_helper.data["session"] = session
