from domain.leagues import Role, User


class UserRepository():

    async def add_role(self, role_id, role_name):
        return await Role.create(role_id=role_id, name=role_name)

    async def get_role(self, role_name) -> Role:
        return await Role.query.where(Role.name == role_name).gino.first()

    async def get_role_by_id(self, role_id) -> Role:
        return await Role.query.where(Role.role_id == role_id).gino.first()

    async def create_user(self, discord_id, gu_user_name, gu_user_id):
        return await User.create(discord_id=discord_id, gu_user_name=gu_user_name, gu_user_id=gu_user_id)

    async def get_user(self, discord_id):
        return await User.query.where(User.discord_id == discord_id).gino.all()
