from domain.leagues import Role, User, LeagueUser
from sqlalchemy import and_

class UserRepository():

    async def add_role(self, role_id, role_name):
        return await Role.create(role_id=role_id, name=role_name)

    async def get_role(self, role_name) -> Role:
        return await Role.query.where(Role.name == role_name).gino.first()

    async def get_role_by_id(self, role_id) -> Role:
        return await Role.query.where(Role.role_id == role_id).gino.first()

    async def create_user(self, discord_id, gu_user_name, gu_user_id, wallet_address):
        return await User.create(discord_id=discord_id, gu_user_name=gu_user_name,
                                 gu_user_id=gu_user_id, wallet_address=wallet_address)

    async def get_user(self, discord_id):
        return await User.query.where(User.discord_id == discord_id).gino.first()

    async def get_league_user(self, discord_id, league_id) -> LeagueUser:
        return await LeagueUser.query.where(and_(LeagueUser.user_id == discord_id, LeagueUser.league_id == league_id)).gino.first()

    async def get_league_users(self, league_id) -> LeagueUser:
        return await LeagueUser.query.where(LeagueUser.league_id == league_id).gino.all()

    async def update_league_user(self, league_user: LeagueUser, updates):
        return await league_user.update(**updates).apply()