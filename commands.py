import requests
import os

APPLICATION_ID = os.environ.get("DISCORD_APPLICATION_ID")
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

headers = {
    "Authorization": "Bot " + BOT_TOKEN
}
print(headers)

data = [{
    "name": "test",
    "type": 1,
    "description": "Testing Jimmy out what up",
    "options": [
        {
            "name": "huh",
            "description": "what you wanna tell me",
            "type": 3,
            "required": True,
        }
    ]
},
    {
        "name": "create-league",
        "type": 1,
        "description": "Starts process to create new league.",
    }
]


response = requests.put(f"https://discord.com/api/v10/applications/{APPLICATION_ID}/commands", json=data, headers=headers)
print(response.json())
print(response.status_code)