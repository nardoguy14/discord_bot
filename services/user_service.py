from domain.permissions import Permissions
from discord_apis import add_guild_role
from repositories.user_repository import UserRepository


class UserService():

    user_repository = UserRepository()

    async def add_user_role(self, guild_id, role_name, permission_name):
        role_id, role_name = add_guild_role(guild_id=guild_id, role_name=role_name,
                                  permissions=Permissions().get_permission_id(permission_name))
        result = await self.user_repository.add_role(role_id, role_name)
        return result

