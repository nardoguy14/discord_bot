import pprint
from aio_celery import Celery
import asyncio
import uuid
import contextlib

from discord_interactions import InteractionResponseType
from domain.leagues import LeagueUser, User
from domain.matches import Match, MatchStatus
from repositories.base_repository import postgres_base_repo
from repositories.matches_repository import MatchesRepository
from services.matches_service import MatchesService
from services.user_service import UserService
from util.discord_apis import (create_channel, get_role, delete_channel, edit_message,
                               modify_channel_permissions, get_guild_channel, create_message, get_guild_channels,
                               get_channel_messages)
from repositories.leagues_repository import LeaguesRepository
import os
from util.gu_apis import get_matches

REDIS_HOST = os.environ.get("REDIS_HOST")

celery = Celery()

print("setup WOUUUUU")
celery.conf.update(
    broker_url=f"amqp://guest:guest@{REDIS_HOST}:5672/"
)


print("broker url")

GUILD_ID = os.environ.get("DISCORD_GUILD_ID")
everyone_role = get_role(GUILD_ID, "@everyone")
matches_repository = MatchesRepository()
matches_service = MatchesService()
leagues_repository = LeaguesRepository()
users_service = UserService()

@celery.define_app_context
@contextlib.asynccontextmanager
async def setup_context():
    db = await postgres_base_repo.connect()
    yield db


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

            matchmaking_channel = create_channel(GUILD_ID, f"🃏matchmaking--{uuid.uuid4().hex[:4]}", permissions,
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
            await matches_repository.set_match_status(match, MatchStatus.WAITING_READY_UP)
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
    match = await matches_repository.get_match_by_discord_id(discord_channel_id)
    await matches_repository.set_match_status(match, MatchStatus.MATCH_BEING_PLAYED)
    countdown = 60 * 5
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


@celery.task(name='ask-for-decks', ignore_result=True)
async def ask_for_decks(discord_channel_id):
    match = await matches_repository.get_match_by_discord_id(discord_channel_id)
    await matches_repository.set_match_status(match, MatchStatus.WAITING_FOR_DECKS)
    countdown = 60 * 5
    codes_set = False
    create_message(discord_channel_id, "Please submit decks now using `/submit-deck`")
    message = create_message(discord_channel_id, f"Waiting {countdown} seconds...")
    while countdown > 0:
        await asyncio.sleep(1)
        print(f"ask for decks {countdown}")
        countdown -= 1
        match = await matches_repository.get_match_by_discord_id(discord_channel_id)
        if match.deck_code_1 is not None and match.deck_code_2 is not None:
            codes_set = True
            break
        edit_message(discord_channel_id, message['id'], f"Waiting {countdown} seconds...")

    if codes_set:
        await handle_finished_game(discord_channel_id)
        await auto_close_channel.delay(discord_channel_id)
    else:
        create_message(discord_channel_id, message="Decks have not been submitted successfully. Please submit them. Waiting again.")
        await ask_for_decks.delay(discord_channel_id)


@celery.task(name='auto-close-channel', ignore_result=True)
async def auto_close_channel(discord_channel_id):
    match = await matches_repository.get_match_by_discord_id(discord_channel_id)
    await matches_repository.set_match_status(match, MatchStatus.GAME_FINISHED)
    countdown = 60 * 2
    message = create_message(discord_channel_id, f"Channel will close in {countdown} seconds.")
    while countdown > 0:
        await asyncio.sleep(1)
        print(f"will auto close in {countdown}")
        countdown -= 1
        edit_message(discord_channel_id, message['id'], f"Channel will close in {countdown} seconds.")
    delete_channel(discord_channel_id)


async def handle_finished_game(discord_channel_id):
    match = await matches_repository.get_match_by_discord_id(discord_channel_id)
    player_1: User = await users_service.get_user_by_discord_id(match.player_id_1)
    player_2: User = await users_service.get_user_by_discord_id(match.player_id_2)
    player_1_matches = get_matches(player_1.gu_user_id)
    player_2_matches = get_matches(player_2.gu_user_id)

    league_user_1 = await users_service.get_league_user(player_1.discord_id, match.league_id)
    league_user_2 = await users_service.get_league_user(player_2.discord_id, match.league_id)

    latest_match_1 = player_1_matches['records'][0]
    latest_match_2 = player_2_matches['records'][0]

    print("the two matches results are: ")
    pprint.pprint(latest_match_1)
    print("and")
    pprint.pprint(latest_match_2)

    latest_match = None
    if latest_match_2['start_time'] > latest_match_1['start_time']:
        latest_match = latest_match_2
    else:
        latest_match = latest_match_1



    player_1_won = False
    player_2_won = False
    if player_1.gu_user_id == str(latest_match['player_won']):
        print('player 1 won')
        player_1_won = True
    elif player_1.gu_user_id == str(latest_match['player_lost']):
        print('player 2 won')
        player_2_won = True
    else:
        print("the player won value does not align with any user")

    league_user_1.ranking = float(league_user_1.ranking)
    league_user_2.ranking = float(league_user_2.ranking)
    if league_user_1.ranking > league_user_2.ranking and player_1_won:
        change_in_elo = (1.0/ (1.3 + abs(league_user_1.ranking - league_user_2.ranking)))
        player_1_new_elo = league_user_1.ranking + change_in_elo
        player_2_new_elo = league_user_2.ranking - change_in_elo
    elif league_user_1.ranking < league_user_2.ranking and player_1_won:
        change_in_elo_winner = (abs(league_user_1.ranking - league_user_2.ranking)/ (0.75 + abs(league_user_1.ranking - league_user_2.ranking)))
        change_in_elo_loser = (abs(league_user_1.ranking - league_user_2.ranking)/ (1.0 + abs(league_user_1.ranking - league_user_2.ranking)))
        player_1_new_elo = league_user_1.ranking + change_in_elo_winner
        player_2_new_elo = league_user_2.ranking - change_in_elo_loser
    elif league_user_2.ranking > league_user_1.ranking and player_2_won:
        change_in_elo = (1.0/ (1.3 + abs(league_user_1.ranking - league_user_2.ranking)))
        player_2_new_elo = league_user_2.ranking + change_in_elo
        player_1_new_elo = league_user_1.ranking - change_in_elo
    elif league_user_2.ranking < league_user_1.ranking and player_2_won:
        change_in_elo_winner = (abs(league_user_1.ranking - league_user_2.ranking)/ (0.75 + abs(league_user_1.ranking - league_user_2.ranking)))
        change_in_elo_loser = (abs(league_user_1.ranking - league_user_2.ranking)/ (1.0 + abs(league_user_1.ranking - league_user_2.ranking)))
        player_2_new_elo = league_user_2.ranking + change_in_elo_winner
        player_1_new_elo = league_user_1.ranking - change_in_elo_loser

    await users_service.update_league_user(league_user_1, {'ranking': player_1_new_elo})
    await users_service.update_league_user(league_user_2, {'ranking': player_2_new_elo})

    winner = None
    if player_1_won:
        winner = player_1.gu_user_name
    else:
        winner = player_2.gu_user_name

    message = f"""
Game is set. \n
Player: {winner} won.🎉🎊🥳\n
New elo scores are:\n
    Player1 {player_1.gu_user_name}: {player_1_new_elo}\n
    Player2 {player_2.gu_user_name}: {player_2_new_elo}
    """
    create_message(discord_channel_id, message)

    await update_standings(league_user_1.league_id, discord_channel_id)


async def update_standings(league_id, discord_channel_id):
    channel = get_guild_channel(GUILD_ID, discord_channel_id)
    parent_id_needed = channel['parent_id']
    channels = get_guild_channels(GUILD_ID)
    for channel in channels:
        if channel['parent_id'] == parent_id_needed and channel['name'] == 'standings':
            messages = get_channel_messages(channel['id'])
            users = await users_service.get_league_users(league_id)
            sorted_users = sorted(users, key=lambda x: x.ranking)[::-1]
            content = "Current Standings\n\n"
            for index, league_user in enumerate(sorted_users):
                user = await users_service.get_user_by_discord_id(league_user.user_id)
                content += f"{index+1}: {user.gu_user_name}: {round(league_user.ranking, 3)}\n"
            if len(messages) > 0:
                pass
                edit_message(channel['id'], messages[0]['id'], content)
            else:
                create_message(channel['id'], content)
            return


async def get_users_who_match(ranking, disparity, player_id):
    users: list[LeagueUser] = await leagues_repository.get_league_users_within_rank(ranking=ranking, disparity=disparity)
    user_ids = []
    for user in users:
        if user.user_id != player_id:
            user_ids.append(user.user_id)
    return user_ids
