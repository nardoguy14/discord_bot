import os
import pprint
import uuid
from datetime import datetime

from discord_interactions import InteractionResponseType

from domain.leagues import User, League
from repositories.leagues_repository import LeaguesRepository
from services.user_service import UserService
from util.discord_apis import delete_channel, send_deferred_final_message, modify_channel
from util.discord_apis import get_role, create_channel, get_guild_channel_by_name, create_message, get_guild_channel, \
    get_guild_channels
from util.gu_apis import get_user_rank
from util.utils import generate_random_emoji
from celery_worker import celery, add

GUILD_ID = os.environ.get("DISCORD_GUILD_ID")
EVERYONE_ROLE = get_role(GUILD_ID, "@everyone")
HOMIE_USERS = get_role(GUILD_ID, "HOMIE_USERS")
ANNOUNCEMENTS_CHANNEL = get_guild_channel_by_name(GUILD_ID, "announcements")


class LeagueService():
    leagues_repository = LeaguesRepository()
    user_service = UserService()

    async def create_league_interaction(self, body, background_tasks):
        async def handle(body):
            name = body['data']['options'][0]['value']
            kind = body['data']['options'][1]['value']
            start_date = body['data']['options'][2]['value']
            end_date = body['data']['options'][3]['value']
            max_plays_per_week = body['data']['options'][4]['value']
            max_disparity = body['data']['options'][5]['value']
            permissions = [
                {'id': EVERYONE_ROLE['id'], 'type': 0, 'deny': "1024"},
                {'id': HOMIE_USERS['id'], 'type': 0, 'allow': "1024"},
            ]
            category_channel = create_channel(GUILD_ID, f"{name}-League", permissions, guild_type=4, category=True)

            create_channel(GUILD_ID, "Info", permissions, parent_id=category_channel['id'])
            create_channel(GUILD_ID, "General Chat", permissions, parent_id=category_channel['id'])
            create_channel(GUILD_ID, "Standings", permissions, parent_id=category_channel['id'])
            create_channel(GUILD_ID, "Matchmaking", permissions, parent_id=category_channel['id'])

            message = f"""New league `{name}` \nkind: `{kind}`\nstarts `{start_date}`\nends `{end_date}`\nmax plays of `{max_plays_per_week}` per week."""
            create_message(ANNOUNCEMENTS_CHANNEL['id'], message)
            await self.leagues_repository.create_league(name, kind,
                                                        datetime.strptime(start_date, '%Y-%m-%d'),
                                                        datetime.strptime(end_date, '%Y-%m-%d'),
                                                        int(max_plays_per_week),
                                                        max_disparity=max_disparity)
            send_deferred_final_message(body['token'],
                                        f'League `{name}` of kind `{kind}` successfully made!~ {generate_random_emoji()}')
        background_tasks.add_task(handle, body)
        return {
            'type': 5  # 5 indicates a deferred response
        }

    async def join_league(self, body):
        if body['channel']['parent_id'] is not None:
            parent_channel = get_guild_channel(GUILD_ID, body['channel']['parent_id'])
        if body['channel']['parent_id'] is None or body['channel']['name'] != 'general-chat' or "League" not in parent_channel['name']:
            return {
                'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                'data': {
                    'content': f'Can only join leagues in `general-chat` channels within a league category.'
                }
            }
        user_id = body['member']['user']['id']
        user_name = body['member']['user']['username']
        print(f"userid {user_id} username {user_name}")
        league_name = parent_channel['name'].split('-')[0]
        league_opt: list[League] = await self.leagues_repository.get_league(league_name)
        user: User = await self.user_service.get_user_by_discord_id(user_id)
        if len(league_opt) > 0:
            curr_date = datetime.now()
            if league_opt[0].start_date < curr_date <= league_opt[0].end_date:
                return {
                    'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    'data': {
                        'content': f'League has already started. Cannot join. {generate_random_emoji()}'
                    }
                }
            elif league_opt[0].end_date < curr_date:
                return {
                    'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    'data': {
                        'content': f'League has ended. Cannot join. {generate_random_emoji()}'
                    }
                }
            else:
                direct_challenge_ranking = get_user_rank(user)
                await self.leagues_repository.join_league(user_id, league_opt[0].id, direct_challenge_ranking)
                return {
                    'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    'data': {
                        'content': f'User `{user_name}` has joined league `{league_name}` successfully!~ {generate_random_emoji()}'
                    }
                }
        else:
            return {
                'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                'data': {
                    'content': f'Sorry this league: `{league_name}` doesnt exist!~ {generate_random_emoji()}'
                }
            }

    async def delete_league(self, guild_id, body, background_tasks):
        async def handle(guild_id, body):
            league_name = body['data']['options'][0]['value'].lower()
            channels = get_guild_channels(guild_id)
            parents_to_children = {}
            category_channel = None
            for channel in channels:
                if channel['parent_id'] is not None:
                    if channel['parent_id'] in parents_to_children:
                        parents_to_children[channel['parent_id']].append(channel)
                    else:
                        parents_to_children[channel['parent_id']] = [channel]
                if league_name in channel['name'].lower():
                    category_channel = channel
            for subchannel in parents_to_children[category_channel['id']]:
                delete_channel(subchannel['id'])
            delete_channel(category_channel['id'])
            try:
                await self.leagues_repository.delete_league(league_name)
            except Exception as e:
                print(e)
            send_deferred_final_message(body['token'],
                                        f'League `{league_name}`deleted~ {generate_random_emoji()}')
        background_tasks.add_task(handle, guild_id, body)
        return {
            'type': 5  # 5 indicates a deferred response
        }

    async def update_league_dates(self, body):
        league_name = body['data']['options'][0]['value']

        data = body['data']['options']
        if len(data) == 1:
            return {
                'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                'data': {
                    'content': f'`start-date` or `end-date` need to be provided. ~ {generate_random_emoji()}'
                }
            }
        elif len(data) != 3:
            if 'start-date' == data[1]['name']:
                start_date_str = body['data']['options'][1]['value']
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = None
            elif 'end-date' == data[1]['name']:
                end_date_str = body['data']['options'][2]['value']
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                start_date = None
        else:
            start_date_str = body['data']['options'][1]['value']
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')

            end_date_str = body['data']['options'][2]['value']
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        await self.leagues_repository.update_league(league_name=league_name,
                                              start_date=start_date,
                                              end_date=end_date)

        return {
            'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            'data': {
                'content': f'League `{league_name}` dates updated ~ {generate_random_emoji()}'
            }
        }

    async def update_league_name(self, body):
        league_name = body['data']['options'][0]['value']
        new_league_name = body['data']['options'][1]['value']
        channel = get_guild_channel_by_name(GUILD_ID, f"{league_name}-League")
        modify_channel(channel['id'], {'name': f"{new_league_name}-League"})
        await self.leagues_repository.update_league(league_name=league_name,
                                              new_name=new_league_name)
        return {
            'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            'data': {
                'content': f'League `{league_name}` renamed to `{new_league_name}` ~ {generate_random_emoji()}'
            }
        }

    async def update_league_max_plays(self, body):
        league_name = body['data']['options'][0]['value']
        max_plays = body['data']['options'][1]['value']
        await self.leagues_repository.update_league(league_name=league_name,
                                              max_plays=max_plays)
        return {
            'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            'data': {
                'content': f'League `{league_name}` max plays updated to `{max_plays}` a week. ~ {generate_random_emoji()}'
            }
        }

    async def update_league_max_disparity(self, body):
        league_name = body['data']['options'][0]['value']
        max_disparity = body['data']['options'][1]['value']
        await self.leagues_repository.update_league(league_name=league_name,
                                                    max_disparity=max_disparity)
        return {
            'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            'data': {
                'content': f'League `{league_name}` max disparity updated to `{max_disparity}`. ~ {generate_random_emoji()}'
            }
        }

    async def matchmake(self, body):
        async with celery.setup():
            channel = body['channel']
            if channel['name'] != 'matchmaking':
                # cant do that in this channel
                return {
                    'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    'data': {
                        'content': f'Can only execute this in `matchmaking` channel. {generate_random_emoji()}'
                    }
                }
            parent_channel = get_guild_channel(GUILD_ID, channel['parent_id'])
            league = (await self.leagues_repository.get_league(parent_channel['name'].split('-')[0]))[0]


            player_id = body['member']['user']['id']
            user = await self.user_service.get_user_by_discord_id(player_id)
            league_user = await self.user_service.get_league_user(user.discord_id, league.id)


            # await matchweeeeeeeemake.delay(player_id, float(league_user.ranking), league.max_disparity, league.id, channel['parent_id'])
            result = await add.delay(player_id, float(league_user.ranking), float(league.max_disparity), league.id, channel['parent_id'])
            print("did i get here or not")
            print(f"heres the answer {result}")
            # pprint.pprint(body)

