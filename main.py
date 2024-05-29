from functools import wraps
import json
import uuid
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, Response
from uvicorn import run
from discord_interactions import InteractionResponseType, InteractionType
from repositories.leagues_repository import LeaguesRepository
from repositories.base_repository import postgres_base_repo

from middleware import DiscordMiddleware
from utils import generate_random_emoji

app = FastAPI()
app.add_middleware(DiscordMiddleware)
postgres_base_repo.db.init_app(app)
leagues_repository = LeaguesRepository()


@app.post("/api/interactions")
async def interactions(req: Request):
    body = await req.body()
    body = json.loads(body.decode('utf-8'))
    t = body['type']

    if t == InteractionType.APPLICATION_COMMAND:
        name = body['data']['name']
        print(body)

        if name == 'create-league' or name == 'test':
            return {
                "type": InteractionResponseType.MODAL,
                "data": {
                    "custom_id": f"create_league_{uuid.uuid4().hex}",
                    "title": "Make a New League",
                    "components": [
                        {
                            "type": 1,
                            "components": [{
                                "type": 4,
                                "custom_id": "name",
                                "label": "Name",
                                "style": 1,
                                "min_length": 1,
                                "max_length": 200,
                                "placeholder": "Cards Galore League",
                                "required": True
                            }]
                        },
                        {
                            "type": 1,
                            "components": [{
                                "type": 4,
                                "custom_id": "kind",
                                "label": "League Kind",
                                "style": 1,
                                "min_length": 1,
                                "max_length": 200,
                                "placeholder": "Yugi MTG GU Poke!",
                                "required": True
                            }]
                        },
                        {
                            "type": 1,
                            "components": [{
                                "type": 4,
                                "custom_id": "start_date",
                                "label": "Start Date",
                                "style": 1,
                                "min_length": 1,
                                "max_length": 200,
                                "placeholder": "YYYY-MM-DD",
                                "required": True
                            }]
                        },
                        {
                            "type": 1,
                            "components": [{
                                "type": 4,
                                "custom_id": "end_date",
                                "label": "End Date",
                                "style": 1,
                                "min_length": 1,
                                "max_length": 200,
                                "placeholder": "YYYY-MM-DD",
                                "required": True
                            }]
                        }
                    ]
                }
            }

    elif t== InteractionType.MODAL_SUBMIT:
        print(body)
        name = body['data']['components'][0]['components'][0]['value']
        kind = body['data']['components'][1]['components'][0]['value']
        start_date = body['data']['components'][2]['components'][0]['value']
        end_date = body['data']['components'][3]['components'][0]['value']

        await leagues_repository.create_league(name, kind,
                                               datetime.strptime(start_date, '%Y-%m-%d'),
                                               datetime.strptime(end_date, '%Y-%m-%d'))
        return {
            'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            'data': {
                'content': 'Yo WADUP ' + generate_random_emoji()
            }
        }


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)