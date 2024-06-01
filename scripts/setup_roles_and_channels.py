import requests
import json
import os

from discord_apis import (get_guild_channels, modify_channel_permissions,
                          create_channel, create_message, pin_message, get_guild_roles, get_role)
from domain.roles import Role
from scripts.api_commands import create_basic_user_roles

GUILD_ID = os.environ.get("DISCORD_GUILD_ID")
WELCOME_CHANNEL = "welcome"
GENERAL_CHANNEL = "general"

basic_role = create_basic_user_roles(Role.HOMIE_USERS.name, GUILD_ID)['__values__']['role_id']
admin_role = create_basic_user_roles(Role.HOMIE_ADMIN.name, GUILD_ID)['__values__']['role_id']
everyone_role = get_role(GUILD_ID, "@everyone")

welcome_channel_permissions = [
    {'id': everyone_role['id'], 'type': 0, 'allow': "1088", 'deny': "1084479698944"}
]
channel = create_channel(GUILD_ID, WELCOME_CHANNEL, welcome_channel_permissions)
content = """
This is a welcome channel.

React to this post to create a channel to register.
"""
message = create_message(channel['id'], content)
pin_message(channel['id'], message['id'])
discord_channels = get_guild_channels(GUILD_ID)
PUBLIC_ALLOWED_CHANNELS = [GENERAL_CHANNEL]

for channel in discord_channels:
    if channel['name'] == WELCOME_CHANNEL:
        continue
    elif channel['name'] in PUBLIC_ALLOWED_CHANNELS:
        permissions = [
            {'id': everyone_role['id'], 'type': 0, 'allow': "2147486720", 'deny': "532576465088"}
        ]
        modify_channel_permissions(channel['id'], permissions)
    elif (channel['type'] == 0 or channel['type'] == 2) and (channel['name'] != "moderator-only" ):
        permissions = [
            {'id': everyone_role['id'], 'type': 0, 'deny': "1024"},
            {'id': str(basic_role.id), 'type': 0, 'allow': "1024"}
        ]
        modify_channel_permissions(channel['id'], permissions)
