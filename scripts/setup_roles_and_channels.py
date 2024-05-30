import requests
import json
from discord_apis import get_guild_channels, modify_channel_permissions

GUILD_ID = "830235184946872340"


def create_basic_user_roles():
    url = "http://localhost:8000/api/roles"

    payload = json.dumps({
        "guild_id": GUILD_ID,
        "role_name": "BASIC_USER3",
        "permission_name": "BASIC_USER_PERMISSIONS"
    })
    headers = {
        'X-Skip-Check': '1',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    return response.json()

# role_id = create_basic_user_roles()['__values__']['role_id']
channels = []
discord_channels = get_guild_channels(GUILD_ID)

for channel in discord_channels:
    if (channel['type'] == 0 or channel['type'] == 2) and channel['name'] != "general":
        channels.append(channel)


def create_role(id, type, allow):
    type_num = None
    if type == "user":
        type_num = 1
    elif type == "role":
        type_num = 0
    result = {'id': id, 'type': type_num, 'allow': 1024}
    if allow:
        result['allow'] = 1024
    else:
        result['deny'] = 1024
    return result

permissions = [
    create_role(GUILD_ID, "role", allow=False),
    create_role("1245616489734865036", "role", allow=True),
]

for channel in channels:
    modify_channel_permissions(channel['id'], permissions)
