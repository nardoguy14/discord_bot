import json

from fastapi import FastAPI, Request
from uvicorn import run
from discord_interactions import InteractionType

from repositories.base_repository import postgres_base_repo
from interactions.league_interactions import LeagueInteractions

from middleware import DiscordMiddleware

app = FastAPI()
app.add_middleware(DiscordMiddleware)
postgres_base_repo.db.init_app(app)


@app.post("/api/interactions")
async def interactions(req: Request):
    body = await req.body()
    body = json.loads(body.decode('utf-8'))
    t = body['type']
    print(body)
    if t == InteractionType.APPLICATION_COMMAND:
        name = body['data']['name']
        if name == 'create-league':
            return LeagueInteractions().create_league_interaction()

    elif t== InteractionType.MODAL_SUBMIT:
        return await LeagueInteractions().process_create_league_modal_submit(body)



if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)
