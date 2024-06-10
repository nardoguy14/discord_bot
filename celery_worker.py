import pprint
from aio_celery import Celery
import asyncio
import uuid

from domain.leagues import LeagueUser
from domain.matches import Match
from repositories.base_repository import postgres_base_repo
from repositories.matches_repository import MatchesRepository
from util.discord_apis import (create_channel, get_role, delete_channel, edit_message,
                               modify_channel_permissions, get_guild_channel, create_message)
from repositories.leagues_repository import LeaguesRepository
import os


celery = Celery()

celery.conf.update(
    result_backend="redis://localhost:6379/0",
    broker_url="amqp://guest:guest@localhost/"
)

GUILD_ID = os.environ.get("DISCORD_GUILD_ID")
everyone_role = get_role(GUILD_ID, "@everyone")
loop = asyncio.get_event_loop()
loop.run_until_complete(postgres_base_repo.connect())
matches_repository = MatchesRepository()
leagues_repository = LeaguesRepository()


@celery.task(name="add-two-numbe3rs")
async def add(player_id, ranking, disparity, league_id, parent_discord_channel_id):
    uu = uuid.uuid4().hex
    countdown = 60 * 4 # minutes x seconds
    matchmaking_channel = None
    channel_message = None
    created_match = False
    match = None
    while countdown > 0:
        print(f"======countdown: {countdown} {uu}")
        user_ids = await  get_users_who_match(ranking, disparity, player_id)
        if not created_match:
            match = await matches_repository.find_matches(league_id=league_id, player_id_2=player_id, user_ids=user_ids)
        if not match and not created_match:
            print("no matches found : (")
            permissions = [
                {'id': everyone_role['id'], 'type': 0,'deny': "1024"},
                {'id': player_id, 'type': 1, 'allow': "1024"}
            ]

            matchmaking_channel = create_channel(GUILD_ID, f"matchmaking-{uuid.uuid4().hex}", permissions,
                                                 parent_id=parent_discord_channel_id)
            crud_match = await matches_repository.create_match(league_id, player_id, matchmaking_channel['id'])
            create_message(matchmaking_channel['id'], f"Trying to find a match. Remaining time (seconds) to find a match: {countdown}")
            created_match = True
        elif created_match and countdown % 5 == 0:
            print("editing message")
            create_message(matchmaking_channel['id'], f"Trying to find a match. Remaining time (seconds) to find a match: {countdown}")
            existing_match: Match = await matches_repository.get_match(crud_match.id)
            if existing_match.player_id_2:
                print('the match has been updated')
                return

        elif not created_match and match:
            existing_channel = get_guild_channel(GUILD_ID, match.discord_channel_id)
            existing_permissions = existing_channel['permission_overwrites']
            existing_permissions.append({'id': player_id, 'type': 1, 'allow': "1024"})
            modify_channel_permissions(existing_channel['id'], existing_permissions)
            create_message(existing_channel['id'], "Players are matched. Type `/ready-up` to begin the match.")
            return

        print(f"======countdown {uu}")
        await asyncio.sleep(1)
        countdown -= 1
    print("No match found.")
    if matchmaking_channel:
        delete_channel(matchmaking_channel['id'])
    if crud_match:
        await matches_repository.delete_match(crud_match)
    return

async def get_users_who_match(ranking, disparity, player_id):
    users: list[LeagueUser] = await leagues_repository.get_league_users_within_rank(ranking=ranking, disparity=disparity)
    user_ids = []
    for user in users:
        if user.user_id != player_id:
            user_ids.append(user.user_id)
    return user_ids