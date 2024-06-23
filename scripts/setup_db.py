import os

from domain.roles import Role
from scripts.api_commands import create_basic_user_roles

GUILD_ID = os.environ.get("DISCORD_GUILD_ID")

basic_role_id = create_basic_user_roles(Role.HOMIE_USERS.name, GUILD_ID)['__values__']['role_id']
admin_role_id = create_basic_user_roles(Role.HOMIE_ADMIN.name, GUILD_ID)['__values__']['role_id']
