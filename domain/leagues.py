
from repositories.base_repository import postgres_base_repo

from sqlalchemy.sql import func

db = postgres_base_repo.db


class League(db.Model):
    __tablename__ = 'leagues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    kind = db.Column(db.String, nullable=False)
    start_date = db.Column(db.DateTime(), nullable=True)
    end_date = db.Column(db.DateTime(), nullable=True)
    created_at = db.Column(db.DateTime(), nullable=False, server_default=func.now())
    modified_at = db.Column(db.DateTime(), nullable=False, server_default=func.now())

