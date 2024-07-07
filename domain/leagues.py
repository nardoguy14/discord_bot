
from repositories.base_repository import postgres_base_repo

from sqlalchemy.sql import func

db = postgres_base_repo.db


class BaseModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(), nullable=False, server_default=func.now())
    modified_at = db.Column(db.DateTime(), nullable=False, server_default=func.now())


class League(BaseModel):
    __tablename__ = 'leagues'
    name = db.Column(db.String, nullable=False)
    kind = db.Column(db.String, nullable=False)
    start_date = db.Column(db.DateTime(), nullable=True)
    end_date = db.Column(db.DateTime(), nullable=True)
    max_plays_per_week = db.Column(db.Integer, nullable=True)
    max_disparity = db.Column(db.DECIMAL, nullable=True)
    rules = db.Column(db.Text, nullable=True)


class LeagueUser(BaseModel):
    __tablename__ = 'league_users'
    user_id = db.Column(db.String, nullable=False)
    league_id = db.Column(db.Integer, nullable=False)
    ranking = db.Column(db.DECIMAL, nullable=True)


class Role(BaseModel):
    __tablename__ = 'roles'
    name = db.Column(db.String, nullable=False)
    role_id = db.Column(db.Integer, nullable=False)


class User(BaseModel):
    __tablename__ = 'users'
    discord_id = db.Column(db.String, nullable=False)
    gu_user_name = db.Column(db.String, nullable=False)
    gu_user_id = db.Column(db.String, nullable=False)
    wallet_address = db.Column(db.String, nullable=True)
