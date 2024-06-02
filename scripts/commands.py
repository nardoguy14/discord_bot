import requests
import os

APPLICATION_ID = os.environ.get("DISCORD_APPLICATION_ID")
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

headers = {
    "Authorization": "Bot " + BOT_TOKEN
}
print(headers)

data = [
    {
        "name": "create-league",
        "type": 1,
        "description": "Starts process to create new league.",
    },
    {
        "name": "join-league",
        "type": 1,
        "description": "Join an existing league."
    },
    {
        "name": "register",
        "type": 1,
        "description": "Join the discord.",
        "options": [
            {
                "name": "gu_username",
                "description": "Whats your Guardians Unchained username?",
                "type": 3,
                "required": True,
            },
            {
                "name": "gu_id",
                "description": "Whats your Guardians Unchained id?",
                "type": 3,
                "required": True,
            }
        ]
    }
]


response = requests.put(f"https://discord.com/api/v10/applications/{APPLICATION_ID}/commands", json=data, headers=headers)
print(response.json())
print(response.status_code)