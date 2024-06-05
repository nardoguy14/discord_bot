import json
import os

from fastapi import FastAPI, Request, BackgroundTasks
from uvicorn import run
from discord_interactions import InteractionType

from repositories.base_repository import postgres_base_repo
from services.league_service import LeagueService

from util.middleware import DiscordMiddleware, check_role
from services.user_service import UserService

user_service = UserService()

app = FastAPI()
app.add_middleware(DiscordMiddleware)
postgres_base_repo.db.init_app(app)
league_service = LeagueService()

GUILD_ID = os.environ.get("DISCORD_GUILD_ID")

@app.post("/api/interactions")
@check_role()
async def interactions(req: Request, backgorund_tasks: BackgroundTasks):
    body = await req.body()
    body = json.loads(body.decode('utf-8'))
    t = body['type']
    print(body)
    if t == InteractionType.APPLICATION_COMMAND:
        name = body['data']['name']
        if name == 'create-league':
            return await league_service.create_league_interaction(body, backgorund_tasks)
        elif name == 'join-league':
            return await league_service.join_league(body)
        elif name == 'register':
            return await user_service.register_user(body)
        elif name == 'delete-league':
            return await league_service.delete_league(GUILD_ID, body, backgorund_tasks)
        elif name == 'update-league-dates':
            return await league_service.update_league_dates(body)
        elif name == 'update-league-name':
            return await league_service.update_league_name(body)
        elif name == 'update-league-max-plays':
            return await league_service.update_league_max_plays(body)
        elif name == 'update-league-rank-disparity':
            return await league_service.update_league_max_disparity(body)

    elif t == InteractionType.MODAL_SUBMIT:
        pass
@app.post("/api/roles")
async def add_role(req: Request):
    body = await req.body()
    body = json.loads(body.decode('utf-8'))
    return await user_service.add_user_role(body['guild_id'], body['role_name'], body['permission_name'])

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)
