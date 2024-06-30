import os

from repositories.base_repository import postgres_base_repo
from util.discord_apis import (get_guild_channels, modify_channel_permissions,
                               create_channel, create_message, pin_message, get_role)
from domain.roles import Role
from scripts.api_commands import create_basic_user_roles
from services.user_service import UserService

GUILD_ID = os.environ.get("DISCORD_GUILD_ID")
GETTING_STARTED_CHANNEL = "getting-started"
GENERAL_CHANNEL = "general"
ANNOUNCEMENTS_CHANNEL = "announcements"
ADMIN_ACTIONS_CHANNEL = "admin-actions"
DISPUTES = 'disputes'

async def main():
    await postgres_base_repo.connect()
    user_service = UserService()
    home_users_role = await user_service.get_role(Role.HOMIE_USERS.name)
    admin_user_role = await user_service.get_role(Role.HOMIE_ADMIN.name)
    admin_role_id = admin_user_role.role_id
    basic_role_id = home_users_role.role_id




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

    create_channel(GUILD_ID, ADMIN_ACTIONS_CHANNEL, admin_permissions)


    def setup_getting_started_channel():
        getting_started_channel = create_channel(GUILD_ID, GETTING_STARTED_CHANNEL, can_view_but_cant_message_channel_permissions)
        content = """
        Please react to this message. 
        
        Doing so will create a separate channel named `{mention}-register`.
        
        Once there you can execute `/register gu_username gu_id`.
        
        This will give you access to the rest of the channels.
        """.replace("\t", "")
        message = create_message(getting_started_channel['id'], content)
        pin_message(getting_started_channel['id'], message['id'])


    setup_getting_started_channel()
    discord_channels = get_guild_channels(GUILD_ID)
    PUBLIC_ALLOWED_CHANNELS = [GENERAL_CHANNEL]

    for channel in discord_channels:
        if channel['name'] == GETTING_STARTED_CHANNEL:
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


import asyncio
loop = asyncio.get_event_loop()
loop.run_until_complete(main())