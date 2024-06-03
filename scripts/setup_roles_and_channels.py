import os

from discord_apis import (get_guild_channels, modify_channel_permissions,
                          create_channel, create_message, pin_message, get_guild_roles, get_role)
from domain.roles import Role
from scripts.api_commands import create_basic_user_roles

GUILD_ID = os.environ.get("DISCORD_GUILD_ID")
WELCOME_CHANNEL = "welcome"
GENERAL_CHANNEL = "general"
ANNOUNCEMENTS_CHANNEL = "announcements"
ADMIN_ACTIONS_CHANNEL = "admin-actions"

basic_role_id = create_basic_user_roles(Role.HOMIE_USERS.name, GUILD_ID)['__values__']['role_id']
admin_role_id = create_basic_user_roles(Role.HOMIE_ADMIN.name, GUILD_ID)['__values__']['role_id']
everyone_role = get_role(GUILD_ID, "@everyone")

can_view_but_cant_message_channel_permissions = [
    {'id': everyone_role['id'], 'type': 0, 'allow': "1088", 'deny': "1084479698944"}
]

announcement_channel = create_channel(GUILD_ID, ANNOUNCEMENTS_CHANNEL, can_view_but_cant_message_channel_permissions)
admin_permissions = [
    {'id': everyone_role['id'], 'type': 0, 'deny': "1024"},
    {'id': admin_role_id, 'type': 0, 'allow': "1024"}
]
admin_actions_channel = create_channel(GUILD_ID, ADMIN_ACTIONS_CHANNEL, admin_permissions)

def setup_welcome_channel():
    welcome_channel = create_channel(GUILD_ID, WELCOME_CHANNEL, can_view_but_cant_message_channel_permissions)
    content = """
    This is a welcome channel.
    
    React to this post to create a channel to register.
    """.replace("\t", "")
    message = create_message(welcome_channel['id'], content)
    pin_message(welcome_channel['id'], message['id'])


setup_welcome_channel()
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
    elif (channel['type'] == 0 or channel['type'] == 2) and (channel['name'] != "moderator-only" and
                                                             channel['name'] != ADMIN_ACTIONS_CHANNEL):
        permissions = [
            {'id': everyone_role['id'], 'type': 0, 'deny': "1024"},
            {'id': basic_role_id, 'type': 0, 'allow': "1024"}
        ]
        modify_channel_permissions(channel['id'], permissions)
