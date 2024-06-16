import os
from gino_starlette import Gino
from gino import Gino as BaseGino

DATABASE_URL = f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}:5432/{os.environ['POSTGRES_DB']}"


class PostgresBaseRepository():

    def __init__(self):
        if "USING_FAST_API" not in os.environ:
            self.db = BaseGino()
        else:
            self.db = Gino(dsn=DATABASE_URL)

    async def connect(self):
        if "USING_FAST_API" not in os.environ:
            print(DATABASE_URL)
            await self.db.set_bind(DATABASE_URL)
            print("binded")
            print(DATABASE_URL)
            return self.db


postgres_base_repo = PostgresBaseRepository()
