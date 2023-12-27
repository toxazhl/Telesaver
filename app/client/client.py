import pyrogram
from pyrogram_patch import patch
from sqlalchemy.orm import sessionmaker

from .handlers import on_delete_message, on_edit_message, on_message
from .middlewares.db import DbSessionMiddleware
from .middlewares.pyro_bot import PyroBotMiddleware


class Client:
    def __init__(
        self,
        session_name: str,
        api_id: int | str,
        api_hash: str,
        pyro_bot: pyrogram.Client,
        db_pool: sessionmaker,
    ) -> None:
        self.client = pyrogram.Client(session_name, api_id, api_hash)
        self.patch_manager = patch(self.client)
        self.patch_manager.include_middleware(DbSessionMiddleware(db_pool))
        self.patch_manager.include_middleware(PyroBotMiddleware(pyro_bot))

        on_message.setup_routers(self.client)
        on_edit_message.setup_routers(self.client)
        on_delete_message.setup_routers(self.client)

    async def run(self) -> None:
        await self.client.start()

    async def stop(self) -> None:
        try:
            await self.client.stop()
        except ConnectionError:
            pass
