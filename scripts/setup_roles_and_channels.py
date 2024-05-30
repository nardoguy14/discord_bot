import requests
import json
from discord_apis import get_guild_channels, modify_channel_permissions, create_role
from domain.roles import Role

GUILD_ID = "830235184946872340"
EVERYONE_ROLE_ID = "830235184946872340"

def create_basic_user_roles():
    url = "http://localhost:8000/api/roles"

    payload = json.dumps({
        "guild_id": GUILD_ID,
        "role_name": Role.HOMIE_USERS.name,
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
discord_channels = get_guild_channels(GUILD_ID)

for channel in discord_channels:
    if channel['name'] == "general":
        permissions = [
            create_role(EVERYONE_ROLE_ID, "role", allow=True),
        ]
        modify_channel_permissions(channel['id'], permissions)
    elif (channel['type'] == 0 or channel['type'] == 2):
        permissions = [
            create_role(EVERYONE_ROLE_ID, "role", allow=False),
            create_role("1245645692173684746", "role", allow=True),
        ]
        modify_channel_permissions(channel['id'], permissions)
