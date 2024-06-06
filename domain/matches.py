from domain.leagues import BaseModel
from repositories.base_repository import postgres_base_repo


db = postgres_base_repo.db


class Match(BaseModel):
    __tablename__ = 'matches'
    player_id = db.Column(db.String, nullable=False)
