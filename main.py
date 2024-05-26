from functools import wraps

from fastapi import FastAPI, Request, HTTPException, Response
from uvicorn import run
from discord_interactions import InteractionResponseType

from middleware import DiscordMiddleware



app = FastAPI()
app.add_middleware(DiscordMiddleware)



@app.post("/api/interactions")
async def interactions(req: Request):

    return {
        'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
        'data': {
            'content': 'Hello world'
        }
    }


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)