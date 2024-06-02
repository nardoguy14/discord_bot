from domain.permissions import Permissions
from discord_apis import add_guild_role, add_guild_role_to_member, get_guild_channels, delete_channel
from domain.roles import Role
from repositories.user_repository import UserRepository
from utils import generate_random_emoji
from discord_interactions import InteractionResponseType


GUILD_ID = "830235184946872340"


class UserService():

    user_repository = UserRepository()

    async def add_user_role(self, guild_id, role_name, permission_name):
        role_id, role_name = add_guild_role(guild_id=guild_id, role_name=role_name,
                                  permissions=Permissions().get_permission_id(permission_name))
        result = await self.user_repository.add_role(role_id, role_name)
        return result


    async def register_user(self, body):
        discord_user_id = body['member']['user']['id']
        gu_user_name = body['data']['options'][0]['value']
        gu_user_id = body['data']['options'][1]['value']
        user_opt: list = await self.user_repository.get_user(discord_user_id)
        if len(user_opt) > 0:
            return {
                'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                'data': {
                    'content': f'User {body["member"]["user"]["username"]} already registered!'
                }
            }
        else:
            role = await self.user_repository.get_role(Role.HOMIE_USERS.name)
            print(role)
            await self.user_repository.create_user(discord_id=discord_user_id, gu_user_name=gu_user_name, gu_user_id=gu_user_id)
            add_guild_role_to_member(GUILD_ID, discord_user_id, role.role_id)
            channels = get_guild_channels(GUILD_ID)
            for channel in channels:
                print(channel['name'])
                print(f"{body['member']['user']['username']}-register")
                if channel['name'] == f"{body['member']['user']['username']}-register":
                    delete_channel(channel['id'])
                    break
