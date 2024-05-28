from functools import wraps
import json
import uuid

from fastapi import FastAPI, Request, HTTPException, Response
from uvicorn import run
from discord_interactions import InteractionResponseType, InteractionType

from middleware import DiscordMiddleware
from utils import generate_random_emoji

app = FastAPI()
app.add_middleware(DiscordMiddleware)



@app.post("/api/interactions")
async def interactions(req: Request):
    body = await req.body()
    body = json.loads(body.decode('utf-8'))
    t = body['type']

    if t == InteractionType.APPLICATION_COMMAND:
        name = body['data']['name']
        print(body)

        if name == 'test':
            return {
                "type": InteractionResponseType.MODAL,
                "data": {
                    "custom_id": uuid.uuid4().hex,
                    "title": "WHAT UP JIMMY",
                    "components": [{
                        "type": 1,
                        "components": [{
                            "type": 4,
                            "custom_id": "name",
                            "label": "DuH nAmE",
                            "style": 1,
                            "min_length": 1,
                            "max_length": 4000,
                            "placeholder": "Mah NaMe JiMmAaY",
                            "required": True
                        }]
                    }]
                }
            }

    elif t== InteractionType.MODAL_SUBMIT:
        print(body)
        return {
            'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            'data': {
                'content': 'Yo WADUP ' + generate_random_emoji()
            }
        }


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)