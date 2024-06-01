import requests
import json
from discord_apis import (get_guild_channels, modify_channel_permissions,
                          create_channel, create_message, pin_message)
from domain.roles import EVERYONE_ROLE_ID, GUILD_ID

WELCOME_CHANNEL = "welcome"
GENERAL_CHANNEL = "general"

def create_basic_user_roles(role_name):
    url = "http://localhost:8000/api/roles"
    payload = json.dumps({
        "guild_id": GUILD_ID,
        "role_name": role_name,
        "permission_name": "BASIC_USER_PERMISSIONS"
    })
    headers = {
        'X-Skip-Check': '1',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    return response.json()

# role_id = create_basic_user_roles(Role.HOMIE_USERS.name)['__values__']['role_id']
#role_id = create_basic_user_roles(Role.HOMIE_ADMIN.name)['__values__']['role_id']
welcome_channel_permissions = [
    {'id': EVERYONE_ROLE_ID, 'type': 0, 'allow': "1088", 'deny': "1084479698944"}
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
        print('weeeee')
        continue
    elif channel['name'] in PUBLIC_ALLOWED_CHANNELS:
        permissions = [
            {'id': EVERYONE_ROLE_ID, 'type': 0, 'allow': "2147486720", 'deny': "532576465088"}
        ]
        modify_channel_permissions(channel['id'], permissions)
    elif (channel['type'] == 0 or channel['type'] == 2) and (channel['name'] != "moderator-only" ):
        permissions = [
            {'id': EVERYONE_ROLE_ID, 'type': 0, 'deny': "1024"},
            {'id': "1245645692173684746", 'type': 0, 'allow': "1024"}
        ]
        modify_channel_permissions(channel['id'], permissions)
