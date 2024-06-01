import json
import requests

def create_basic_user_roles(role_name, guild_id):
    url = "http://localhost:8000/api/roles"
    payload = json.dumps({
        "guild_id": guild_id,
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
