import pprint
from aio_celery import Celery
import asyncio
from repositories.base_repository import postgres_base_repo
from repositories.matches_repository import MatchesRepository
from util.discord_apis import (create_channel, get_role, delete_channel, edit_message,
                               modify_channel_permissions, get_guild_channel, create_message)
import os


celery = Celery()

celery.conf.update(
    result_backend="redis://localhost:6379/0",
    broker_url="amqp://guest:guest@localhost/"
)

GUILD_ID = os.environ.get("DISCORD_GUILD_ID")
everyone_role = get_role(GUILD_ID, "@everyone")


# @celery.task(name='match-make-dis-shit')
# async def matchweeeeeeeemake(player_id, ranking, disparity, league_id, parent_discord_channel_id):
#     countdown = 60 * 4 # minutes x seconds
#     print("in hereeeeeeeeee")
    # await postgres_base_repo.connect()
    # matchmaking_channel = None
    # channel_message = None
    # created_match = False
    # match = None
    # while countdown > 0:
    #     print(f"======countdown: {countdown}")
    #     x = MatchesRepository()
    #     matches = await x.find_matches(ranking=ranking, disparity=disparity, league_id=league_id)
    #     if len(matches) == 0:
    #         print("no matches found : (")
    #         permissions = [
    #             {'id': everyone_role['id'], 'type': 0,'deny': "1024"},
    #             {'id': player_id, 'type': 1, 'allow': "1024"}
    #         ]
    #         import uuid
    #         matchmaking_channel = create_channel(GUILD_ID, f"matchmaking-{uuid.uuid4().hex}", permissions,
    #                                              parent_id=parent_discord_channel_id)
    #         crud_match = await x.create_match(league_id, player_id, matchmaking_channel['id'])
    #         channel_message = create_message(matchmaking_channel['id'], f"Trying to find a match. Remaining time (seconds) to find a match: {countdown}")
    #         created_match = True
    #     elif created_match and countdown % 5 == 0:
    #         print("editing message")
    #         create_message(matchmaking_channel['id'], f"Trying to find a match. Remaining time (seconds) to find a match: {countdown}")
    #         # edit_message(matchmaking_channel['id'], channel_message['id'], f"Trying to find a match. Remaining time (seconds) to find a match: {countdown}")
    #     else:
    #         print("elseeeeeee")
    #         for match in matches:
    #             pprint.pprint(match)
    #             if match[0] != player_id:
    #                 existing_channel = get_guild_channel(GUILD_ID, match[1])
    #                 pprint.pprint(existing_channel)
    #                 existing_permissions = existing_channel['permission_overwrites']
    #                 existing_permissions.append({'id': player_id, 'type': 1, 'allow': "1024"})
    #                 modify_channel_permissions(existing_channel['id'], existing_permissions)
    #                 await x.create_match(league_id, player_id, match[1])
    #                 create_message(existing_channel['id'], "Players are matched. Type `/ready-up` to begin the match.")
    #                 return
    #
    #
    #     print(matches)
    #     print(f"======countdown")
    #     await asyncio.sleep(1)
    #     countdown -= 1
    # print("No match found.")
    # if matchmaking_channel:
    #     delete_channel(matchmaking_channel['id'])
    # if crud_match:
    #     print(crud_match)
    #     await x.delete_match(crud_match)


@celery.task(name="add-two-numbe3rs")
async def add(player_id, ranking, disparity, league_id, parent_discord_channel_id):
    print("IM IN HERE!!!!")
    # await asyncio.sleep(5)
    countdown = 60 * 4 # minutes x seconds
    print("in hereeeeeeeeee")
    await postgres_base_repo.connect()
    matchmaking_channel = None
    channel_message = None
    created_match = False
    match = None
    while countdown > 0:
        print(f"======countdown: {countdown}")
        x = MatchesRepository()
        matches = await x.find_matches(ranking=ranking, disparity=disparity, league_id=league_id)
        if len(matches) == 0:
            print("no matches found : (")
            permissions = [
                {'id': everyone_role['id'], 'type': 0,'deny': "1024"},
                {'id': player_id, 'type': 1, 'allow': "1024"}
            ]
            import uuid
            matchmaking_channel = create_channel(GUILD_ID, f"matchmaking-{uuid.uuid4().hex}", permissions,
                                                 parent_id=parent_discord_channel_id)
            crud_match = await x.create_match(league_id, player_id, matchmaking_channel['id'])
            channel_message = create_message(matchmaking_channel['id'], f"Trying to find a match. Remaining time (seconds) to find a match: {countdown}")
            created_match = True
        elif created_match and countdown % 5 == 0:
            print("editing message")
            create_message(matchmaking_channel['id'], f"Trying to find a match. Remaining time (seconds) to find a match: {countdown}")
            # edit_message(matchmaking_channel['id'], channel_message['id'], f"Trying to find a match. Remaining time (seconds) to find a match: {countdown}")
        else:
            print("elseeeeeee")
            for match in matches:
                pprint.pprint(match)
                if match[0] != player_id:
                    existing_channel = get_guild_channel(GUILD_ID, match[1])
                    pprint.pprint(existing_channel)
                    existing_permissions = existing_channel['permission_overwrites']
                    existing_permissions.append({'id': player_id, 'type': 1, 'allow': "1024"})
                    modify_channel_permissions(existing_channel['id'], existing_permissions)
                    await x.create_match(league_id, player_id, match[1])
                    create_message(existing_channel['id'], "Players are matched. Type `/ready-up` to begin the match.")
                    return

        print(matches)
        print(f"======countdown")
        await asyncio.sleep(1)
        countdown -= 1
    print("No match found.")
    if matchmaking_channel:
        delete_channel(matchmaking_channel['id'])
    if crud_match:
        print(crud_match)
        await x.delete_match(crud_match)
    return