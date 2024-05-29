import os
from gino_starlette import Gino


DATABASE_URL = f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}:5432/{os.environ['POSTGRES_DB']}"


class PostgresBaseRepository():

    def __init__(self):
        self.db = Gino(dsn=DATABASE_URL)


postgres_base_repo = PostgresBaseRepository()
