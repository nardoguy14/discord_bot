import requests
import os

APPLICATION_ID = os.environ.get("DISCORD_APPLICATION_ID")
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

headers = {
    "Authorization": "Bot " + BOT_TOKEN
}
print(headers)

CREATE_LEAGUE = {
    "name": "create-league",
    "type": 1,
    "description": "Starts process to create new league.",
    "options": [
        {
            "name": "league-name",
            "description": "Name of the league.",
            "type": 3,
            "required": True,
        },
        {
            "name": "kind",
            "description": "Is it for pokemon, mtg, yugioh, gu, what?",
            "type": 3,
            "required": True,
        },
        {
            "name": "start_date",
            "description": "Whens it start format: YYYY-MM-DD?",
            "type": 3,
            "required": True,
        },
        {
            "name": "end_date",
            "description": "Whens it end format: YYYY-MM-DD?",
            "type": 3,
            "required": True,
        },
        {
            "name": "max-plays-per-week",
            "description": "How many games could a player play a week?",
            "type": 3,
            "required": True,
        },
        {
            "name": "max-disparity",
            "description": "Whats the max level difference between two players?",
            "type": 3,
            "required": True,
        }
    ]
}

JOIN_LEAGUE = {
    "name": "join-league",
    "type": 1,
    "description": "Join an existing league."
}

REGISTER_LEAGUE = {
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
        },
        {
            "name": "wallet_address",
            "description": "Wallet address that will be used to pay for league.",
            "type": 3,
            "required": True
        }
    ]
}

DELETE_LEAGUE = {
    "name": "delete-league",
    "type": 1,
    "description": "Deletes a league and all its subchannels.",
    "options": [
        {
            "name": "league-name",
            "description": "The name of the league category that has subchannels.",
            "type": 3,
            "required": True,
        }
    ]
}

UPDATE_LEAGUE_DATES = {
    "name": "update-league-dates",
    "type": 1,
    "description": "Updates a league's stat and end dates",
    "options": [
        {
            "name": "league-name",
            "description": "leagues name",
            "type": 3,
            "required": True,
        },
        {
            "name": "start-date",
            "description": "start date of league",
            "type": 3,
            "required": False,
        },
        {
            "name": "end-date",
            "description": "end date of league",
            "type": 3,
            "required": False,
        }
    ]
}

UPDATE_LEAGUE_NAME = {
    "name": "update-league-name",
    "type": 1,
    "description": "Updates a league's name",
    "options": [
        {
            "name": "league-name",
            "description": "leagues new name",
            "type": 3,
            "required": True,
        },
        {
            "name": "new-league-name",
            "description": "leagues new name",
            "type": 3,
            "required": True,
        }
    ]
}

UPDATE_LEAGUE_MAX_PLAYS = {
    "name": "update-league-max-plays",
    "type": 1,
    "description": "Max number of plays that can be played per week by a player",
    "options": [
        {
            "name": "league-name",
            "description": "leagues new name",
            "type": 3,
            "required": True,
        },
        {
            "name": "max-plays",
            "description": "number of plays per week",
            "type": 3,
            "required": True,
        }
    ]
}

UPDATE_LEAGUE_MAX_DISPARITY = {
    "name": "update-league-rank-disparity",
    "type": 1,
    "description": "Max difference in players rank that can be allowed for a match to occur.",
    "options": [
        {
            "name": "league-name",
            "description": "leagues new name",
            "type": 3,
            "required": True,
        },
        {
            "name": "max-disparity",
            "description": "max difference in levels allowed",
            "type": 3,
            "required": True,
        }
    ]
}

ACTIVATE_LEAGUE = {
    "name": "activate-league",
    "type": 1,
    "description": "Activates a league regardless of starting or end dates.",
    "options": [
        {
            "name": "league-name",
            "description": "League to activate",
            "type": 3,
            "required": True,
        }
    ]
}

DEACTIVATE_LEAGUE = {
    "name": "deactivate-league",
    "type": 1,
    "description": "Deactivates a league regardless of starting or end dates.",
    "options": [
        {
            "name": "league-name",
            "description": "League to deactivate",
            "type": 3,
            "required": True,
        }
    ]
}

MATCHMAKE = {
    "name": "match-make",
    "type": 1,
    "description": "Starts matchmaking process. To be used within `matchmaking` channel of a league.",
}

READY_UP = {
    "name": "ready-up",
    "type": 1,
    "description": "Ready for a match and prompts other user to ready up too.",
}

SUBMIT_DECK = {
    "name": "submit-deck",
    "type": 1,
    "description": "Submits a deck used in a given match",
    "options": [
        {
            "name": "deck-code",
            "description": "The deck code to submit",
            "type": 3,
            "required": True,
        },
    ]
}

GET_LEAGUE = {
    "name": "get-league",
    "type": 1,
    "description": "Retrieves details of league",
    "options": [
        {
            "name": "league-name",
            "description": "Name of the league youre trying to get details about.",
            "type": 3,
            "required": True,
        },
    ]
}


DISPUTE = {
    "name": "dispute",
    "type": 1,
    "description": "Used to dispute hte result of a given match.",
}

data = [
    CREATE_LEAGUE,
    GET_LEAGUE,
    JOIN_LEAGUE,
    REGISTER_LEAGUE,
    DELETE_LEAGUE,
    UPDATE_LEAGUE_DATES,
    UPDATE_LEAGUE_NAME,
    UPDATE_LEAGUE_MAX_PLAYS,
    UPDATE_LEAGUE_MAX_DISPARITY,
    ACTIVATE_LEAGUE,
    DEACTIVATE_LEAGUE,
    MATCHMAKE,
    READY_UP,
    SUBMIT_DECK,
    DISPUTE
]


response = requests.put(f"https://discord.com/api/v10/applications/{APPLICATION_ID}/commands", json=data, headers=headers)
print(response.json())
print(response.status_code)
