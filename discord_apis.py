import requests
import os
import pprint

BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

DISCORD_HOST = "https://discord.com/api/v10"


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

def create_secret_channel(guild_id, channel_name, user1_id, user2_id):
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}',
        'Content-Type': 'application/json'
    }

    # Create a new channel
    payload = {
        'name': channel_name,
        'type': 0,
        'permission_overwrites': [
            {'id': guild_id, 'type': 0, 'deny': 1024},
            {'id': user1_id, 'type': 1, 'allow': 1024},
            {'id': user2_id, 'type': 1, 'allow': 1024}
        ]
    }
    response = requests.post(f'{DISCORD_HOST}/guilds/{guild_id}/channels', headers=headers, json=payload)
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


def search_guild_members(guild_id, potential_user):
    headers = {
        'Authorization': f'Bot {BOT_TOKEN}'
    }

    # Get the list of members in the guild
    response = requests.get(f'{DISCORD_HOST}/guilds/{guild_id}/members/search',
                            params={'query': potential_user},
                            headers=headers)

    return response.json()
