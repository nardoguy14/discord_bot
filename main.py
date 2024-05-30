import json

from fastapi import FastAPI, Request
from uvicorn import run
from discord_interactions import InteractionType

from repositories.base_repository import postgres_base_repo
from interactions.league_interactions import LeagueInteractions

from middleware import DiscordMiddleware
from services.user_service import UserService

user_service = UserService()

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
        elif name == 'join-league':
            return await LeagueInteractions().join_league(body)
        elif name == 'register':
            return await user_service.register_user(body)

    elif t== InteractionType.MODAL_SUBMIT:
        return await LeagueInteractions().process_create_league_modal_submit(body)

@app.post("/api/roles")
async def add_role(req: Request):
    body = await req.body()
    body = json.loads(body.decode('utf-8'))
    return await user_service.add_user_role(body['guild_id'], body['role_name'], body['permission_name'])

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)
