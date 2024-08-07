from domain.leagues import BaseModel
from repositories.base_repository import postgres_base_repo


db = postgres_base_repo.db


class Match(BaseModel):
    __tablename__ = 'matches'
    status = db.Column(db.String, nullable=True)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'))
    player_id_1 = db.Column(db.String, nullable=False)
    player_id_2 = db.Column(db.String, nullable=True)
    discord_channel_id = db.Column(db.String, nullable=False)
    ready_up_1 = db.Column(db.Boolean, nullable=True)
    ready_up_2 = db.Column(db.Boolean, nullable=True)
    deck_code_1 = db.Column(db.String, nullable=True)
    deck_code_2 = db.Column(db.String, nullable=True)


class MatchStatus():

    MATCH_MAKING = "MATCHMAKING"
    WAITING_READY_UP = "WAITING_READY_UP"
    MATCH_BEING_PLAYED = "MATCH_BEING_PLAYED"
    WAITING_FOR_DECKS = "WAITING_FOR_DECKS"
    GAME_FINISHED = "GAME_FINISHED"