from pyrogram_middleware_patch.types import OnUpdateMiddleware
from sqlalchemy.orm import sessionmaker


class DbSessionMiddleware(OnUpdateMiddleware):
    def __init__(self, session_pool: sessionmaker):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(self, update) -> dict:
        async with self.session_pool() as session:
            return {"session": session}
