import requests
import os
from pprint import pprint

BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

DISCORD_HOST = "https://discord.com/api/v10"


def add_guild_role(guild_id: str, role_name: str, permissions: str):
    endpoint = f"/guilds/{guild_id}/roles"
    full_url = f"{DISCORD_HOST}{endpoint}"
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        "name": role_name,
        "permissions": permissions,
        "hoist": True
    }
    response = requests.post(full_url, headers=headers, json=data)
    response_data = response.json()
    pprint(response_data)
    id = response_data['id']
    name = response_data['name']
    return (id, name)


def add_guild_role_to_member(guild_id, member_id, role_id):
    endpoint = f"/guilds/{guild_id}/members/{member_id}/roles/{role_id}"
    full_url = f"{DISCORD_HOST}{endpoint}"
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}'
    }
    response = requests.put(full_url, headers=headers)
    return response


def add_to_secret_channel(guild_id, channel_id, user_id):
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = {
        'permission_overwrites': [
            {'id': guild_id, 'type': 0, 'deny': 1024},
            {'id': user_id, 'type': 1, 'allow': 1024},
        ]
    }
    response = requests.patch(f'https://discord.com/api/v10/channels/{channel_id}', headers=headers, json=payload)
    print(response.json())
    return


def create_secret_channel(guild_id, role_id, channel_name, user_ids):
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}',
        'Content-Type': 'application/json'
    }
    permissions = [
        {'id': role_id, 'type': 0, 'deny': "1024"}
    ]
    for user_id in user_ids:
        permissions.append({'id': user_id, 'type': 1, 'allow': "1024"})
    # Create a new channel
    payload = {
        'name': channel_name,
        'type': 0,
        'permission_overwrites': permissions
    }
    response = requests.post(f'{DISCORD_HOST}/guilds/{guild_id}/channels', headers=headers, json=payload)
    channel = response.json()
    print(channel)
    return channel


def delete_channel(channel_id):
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}',
        'Content-Type': 'application/json'
    }
    response = requests.delete(f'{DISCORD_HOST}/channels/{channel_id}', headers=headers)
    channel = response.json()
    print(channel)
    return channel


def get_guild_users(guild_id, limit=1):
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}'
    }

    # Get the list of members in the guild
    response = requests.get(f'{DISCORD_HOST}/guilds/{guild_id}/members',
                            params={'limit': limit},
                            headers=headers)
    members = response.json()
    print(response.headers)
    return members


def get_guild_roles(guild_id, limit=1):
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}'
    }

    # Get the list of members in the guild
    response = requests.get(f'{DISCORD_HOST}/guilds/{guild_id}/roles',
                            headers=headers)
    roles = response.json()
    print(response.headers)
    return roles


def search_guild_members(guild_id, potential_user):
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}'
    }

    # Get the list of members in the guild
    response = requests.get(f'{DISCORD_HOST}/guilds/{guild_id}/members/search',
                            params={'query': potential_user},
                            headers=headers)

    return response.json()


def get_guild_channels(guild_id):
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}'
    }

    # Get the list of members in the guild
    response = requests.get(f'{DISCORD_HOST}/guilds/{guild_id}/channels',
                        headers=headers)
    pprint(response.json())
    return response.json()


def create_channel(guild_id, channel_name, permissions):
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}'
    }
    full_url = f"{DISCORD_HOST}/guilds/{guild_id}/channels"
    data = {
        "name": channel_name,
        "type": 0,
        "topic": "Text",
        "permission_overwrites" : permissions
    }
    response = requests.post(full_url, headers=headers, json=data)
    channel = response.json()
    pprint(channel)
    return channel


def create_message(channel_id, message):
    endpoint = f"/channels/{channel_id}/messages"
    full_url = f"{DISCORD_HOST}{endpoint}"
    data = {
        "content": message
    }
    response = requests.post(full_url, headers={'Authorization': f'Bot {BOT_TOKEN}'}, json=data)
    message = response.json()
    pprint(message)
    return message


def pin_message(channel_id, message_id):
    endpoint = f"/channels/{channel_id}/pins/{message_id}"
    full_url = f"{DISCORD_HOST}{endpoint}"
    response = requests.put(full_url, headers={'Authorization': f'Bot {BOT_TOKEN}'})
    print(response.status_code)
    return response


def modify_channel_permissions(channel_id, permissions):
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}'
    }
    data = {
        'permission_overwrites': permissions
    }

    response = requests.patch(f'{DISCORD_HOST}/channels/{channel_id}',
                            json=data,
                            headers=headers)
    j = response.json()
    pprint(j)
    return j


def create_role(id, type, allow):
    type_num = None
    if type == "user":
        type_num = 1
    elif type == "role":
        type_num = 0
    result = {'id': id, 'type': type_num, 'allow': 1024}
    if allow:
        result['allow'] = "962073160768"
    else:
        result['deny'] = "603619065329472"
    return result
