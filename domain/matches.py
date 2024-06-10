from domain.leagues import BaseModel
from repositories.base_repository import postgres_base_repo


db = postgres_base_repo.db


class Match(BaseModel):
    __tablename__ = 'matches'
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'))
    player_id_1 = db.Column(db.String, nullable=False)
    player_id_2 = db.Column(db.String, nullable=True)
    discord_channel_id = db.Column(db.String, nullable=False)
