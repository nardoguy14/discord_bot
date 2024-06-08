from domain.leagues import BaseModel
from repositories.base_repository import postgres_base_repo


db = postgres_base_repo.db


class Match(BaseModel):
    __tablename__ = 'matches'
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'))
    player_id = db.Column(db.String, nullable=False)
    discord_channel_id = db.Column(db.String, nullable=False)
