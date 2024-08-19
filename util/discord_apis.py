import requests
import os
from pprint import pprint

BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
DISCORD_APPLICATION_ID = os.environ.get("DISCORD_APPLICATION_ID")
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

def delete_guild_role_to_member(guild_id, member_id, role_id):
    endpoint = f"/guilds/{guild_id}/members/{member_id}/roles/{role_id}"
    full_url = f"{DISCORD_HOST}{endpoint}"
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}'
    }
    response = requests.delete(full_url, headers=headers)
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

def get_role(guild_id, role_name):
    roles = get_guild_roles(guild_id)
    for role in roles:
        if role['name'] == role_name:
            return role


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


def get_guild_channel(guild_id, channel_id):
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}'
    }
    response = requests.get(f'{DISCORD_HOST}/channels/{channel_id}',
                            headers=headers)
    pprint(response.json())
    return response.json()


def get_guild_channel_by_name(guild_id, channel_name):
    channels = get_guild_channels(guild_id)
    for channel in channels:
        if channel['name'] == channel_name:
            return channel


def get_channel_messages(channel_id):
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}'
    }

    # Get the list of members in the guild
    response = requests.get(f'{DISCORD_HOST}/channels/{channel_id}/messages',
                            headers=headers)
    messages = response.json()
    pprint(messages)
    return messages


def create_channel(guild_id, channel_name, permissions, guild_type=0, parent_id=None, category=False):
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}'
    }
    full_url = f"{DISCORD_HOST}/guilds/{guild_id}/channels"
    data = {
        "name": channel_name,
        "type": guild_type,
        "topic": "Text",
        "permission_overwrites": permissions,
    }
    if parent_id:
        data['parent_id'] = parent_id
    if category:
        del data['topic']

    response = requests.post(full_url, headers=headers, json=data)
    channel = response.json()
    pprint(channel)
    return channel


def create_message(channel_id, message, components=None):
    endpoint = f"/channels/{channel_id}/messages"
    full_url = f"{DISCORD_HOST}{endpoint}"
    data = {
        "content": message
    }
    if components:
        data['components'] = components
    response = requests.post(full_url, headers={'Authorization': f'Bot {BOT_TOKEN}'}, json=data)
    message = response.json()
    pprint(message)
    return message


def edit_message(channel_id, message_id, message):
    endpoint = f"/channels/{channel_id}/messages/{message_id}"
    full_url = f"{DISCORD_HOST}{endpoint}"
    data = {
        "content": message
    }
    response = requests.patch(full_url, headers={'Authorization': f'Bot {BOT_TOKEN}'}, json=data)
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


def modify_channel(channel_id, args):
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}'
    }
    response = requests.patch(f'{DISCORD_HOST}/channels/{channel_id}',
                              json=args,
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


def send_deferred_final_message(interaction_token, content):
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}',
        'Content-Type': 'application/json'
    }
    full_url = f'{DISCORD_HOST}/webhooks/{DISCORD_APPLICATION_ID}/{interaction_token}/messages/@original'
    payload = {
        'content': content
    }
    response = requests.patch(full_url, json=payload, headers=headers)
    pprint(response.json())
    response.raise_for_status()


def get_main_league_channel(channels, league_name):
    for channel in channels:
        if channel['name'] == f"{league_name}-League":
            return channel


def get_child_league_channel(channels, league_name, child_channel):
    parent_channel = get_main_league_channel(channels, league_name)
    print("parent channel")
    print(parent_channel)
    for channel in channels:
        print("channel")
        print(channel)
        if 'parent_id' in channel and channel['parent_id'] == parent_channel['id'] and channel['name'] == child_channel:
            return channel