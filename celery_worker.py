import pprint
from aio_celery import Celery
import asyncio
import uuid

from domain.leagues import LeagueUser, User
from domain.matches import Match
from repositories.base_repository import postgres_base_repo
from repositories.matches_repository import MatchesRepository
from services.matches_service import MatchesService
from services.user_service import UserService
from util.discord_apis import (create_channel, get_role, delete_channel, edit_message,
                               modify_channel_permissions, get_guild_channel, create_message)
from repositories.leagues_repository import LeaguesRepository
import os


celery = Celery()

celery.conf.update(
    result_backend="redis://localhost:6379/0",
    broker_url="amqp://guest:guest@localhost:5672/"
)

GUILD_ID = os.environ.get("DISCORD_GUILD_ID")
everyone_role = get_role(GUILD_ID, "@everyone")
loop = asyncio.get_event_loop()
loop.run_until_complete(postgres_base_repo.connect())
matches_repository = MatchesRepository()
matches_service = MatchesService()
leagues_repository = LeaguesRepository()
users_service = UserService()


@celery.task(name="add-two-numbers")
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
            existing_match: Match = await matches_repository.get_match(crud_match.id)
            if existing_match.player_id_2:
                print('the match has been updated')
                return
            create_message(matchmaking_channel['id'], f"Trying to find a match. Remaining time (seconds) to find a match: {countdown}")

        elif not created_match and match:
            existing_channel = get_guild_channel(GUILD_ID, match.discord_channel_id)
            existing_permissions = existing_channel['permission_overwrites']
            existing_permissions.append({'id': player_id, 'type': 1, 'allow': "1024"})
            modify_channel_permissions(existing_channel['id'], existing_permissions)

            league_player_1: LeagueUser = await leagues_repository.get_league_user(match.league_id, match.player_id_1)
            league_player_2: LeagueUser = await leagues_repository.get_league_user(match.league_id, match.player_id_2)

            player_1: User = await users_service.get_user_by_discord_id(match.player_id_1)
            player_2: User = await users_service.get_user_by_discord_id(match.player_id_2)

            create_message(existing_channel['id'], "Players are matched. \n"
                                                   f"Player `{player_1.gu_user_name}` has elo score of `{round(league_player_1.ranking, 3)}`\n"
                                                   f"Player `{player_2.gu_user_name}` has elo score of `{round(league_player_2.ranking, 3)}`\n"
                                                   "Type `/ready-up` to begin the match.")
            await ready_up.apply_async(args=[match.league_id, match.discord_channel_id])
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


@celery.task(name="wait-for-ready-up", ignore_result=True)
async def ready_up(league_id, discord_channel_id):
    countdown = 60 * 60
    def message_str(countdown): return f"Waiting for players to ready up. Seconds remaining: {countdown}"
    message = create_message(discord_channel_id, message_str(countdown))
    match = None
    while countdown > 0:
        if countdown % 10 == 0:
            match = await matches_repository.get_match_by_discord_id(discord_channel_id)
            if match.ready_up_1 and match.ready_up_2:
                join_code = uuid.uuid4().hex[:10]
                create_message(discord_channel_id, f"You can now join the game with code: `{join_code}`")
                await check_for_match_completion.apply_async(args=[discord_channel_id])
                return
            else:
                if countdown % 10 == 0:
                    edit_message(discord_channel_id, message['id'], message_str(countdown))
        await asyncio.sleep(1)
        countdown -= 1
    create_message(discord_channel_id, "Users didnt ready up in time. Please type `ready-up` to try again.")
    await matches_repository.set_ready(match, match.player_id_2, False)
    await matches_repository.set_ready(match, match.player_id_1, False)
    return

@celery.task(name='check-for-match-completion', ignore_result=True)
async def check_for_match_completion(discord_channel_id):
    countdown = 3 #60 * 5
    while countdown > 0:
        await asyncio.sleep(1)
        print(f"check for match completion {countdown}")
        countdown -= 1
    components = [
        {
            "type": 1,
            "components": [
                {
                    "type": 2,
                    "label": "✅",
                    "style": 1,
                    "custom_id": "GAME_FINISHED"
                }
            ]

        }
    ]
    create_message(discord_channel_id, f"Hey there! Did the game finish? Hit the checkmark if so!", components=components)




async def get_users_who_match(ranking, disparity, player_id):
    users: list[LeagueUser] = await leagues_repository.get_league_users_within_rank(ranking=ranking, disparity=disparity)
    user_ids = []
    for user in users:
        if user.user_id != player_id:
            user_ids.append(user.user_id)
    return user_ids
