import os
import uuid
from datetime import datetime

from discord_interactions import InteractionResponseType

from domain.leagues import User
from repositories.leagues_repository import LeaguesRepository
from services.user_service import UserService
from util.discord_apis import delete_channel, send_deferred_final_message, modify_channel
from util.discord_apis import get_role, create_channel, get_guild_channel_by_name, create_message, get_guild_channel, \
    get_guild_channels
from util.gu_apis import get_user_rank
from util.utils import generate_random_emoji

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
        league_opt = await self.leagues_repository.get_league(league_name)
        user: User = await self.user_service.get_user_by_discord_id(user_id)
        if len(league_opt) > 0:
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
                'content': f'League `{league_name}` dates updated to `{start_date_str}` - `{end_date_str}` ~ {generate_random_emoji()}'
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


{'app_permissions': '2251799813685247', 'application_id': '1244403754502062212', 'authorizing_integration_owners': {'0': '830235184946872340'},
 'channel': {'flags': 0, 'guild_id': '830235184946872340', 'id': '1247607164684468224', 'last_message_id': '1247735880467091508', 'name': 'admin-actions', 'nsfw': False, 'parent_id': None, 'permissions': '2222085186637377', 'position': 7, 'rate_limit_per_user': 0, 'topic': 'Text', 'type': 0}, 'channel_id': '1247607164684468224', 'context': 0,
 'data': {'id': '1245126215342227548', 'name': 'create-league', 'options': [{'name': 'league-name', 'type': 3, 'value': 'aghhhhh'}, {'name': 'kind', 'type': 3, 'value': 'dskfjsdkfs'}, {'name': 'start_date', 'type': 3, 'value': '2022-01-01'}, {'name': 'end_date', 'type': 3, 'value': '2023-01-01'}, {'name': 'max-plays-per-week', 'type': 3, 'value': '10'}, {'name': 'max-disparity', 'type': 3, 'value': '10'}], 'type': 1}, 'entitlement_sku_ids': [], 'entitlements': [], 'guild': {'features': ['COMMUNITY', 'NEWS'], 'id': '830235184946872340', 'locale': 'en-US'}, 'guild_id': '830235184946872340', 'guild_locale': 'en-US',
 'id': '1247736316402204724', 'locale': 'en-US',
 'member': {'avatar': None, 'communication_disabled_until': None, 'deaf': False, 'flags': 1, 'joined_at': '2024-05-31T07:42:42.182000+00:00', 'mute': False, 'nick': None, 'pending': False, 'permissions': '2222085186637377', 'premium_since': None, 'roles': ['1247607160917983253', '1247607159416426567'], 'unusual_dm_activity_until': None, 'user': {'avatar': None, 'avatar_decoration_data': None, 'clan': None, 'discriminator': '0', 'global_name': 'nardotester', 'id': '1245976169694625844', 'public_flags': 0, 'username': 'nardotester'}},
 'token': 'aW50ZXJhY3Rpb246MTI0NzczNjMxNjQwMjIwNDcyNDp3MnlxU2VwWXRoOHpxSmhUN1JpaXJVSFA4SE9yRmxTYndBeUYxTjljRXF3aHR1R2V2S05kNmYySTFORHk4dDV2amR6VlBuWjlTaVZUb2hMNkZGb0Nab0xWZk5jNEZKckhPaFUxVURJYTFaTEU0cXZicWg4d0ljZXdpQnp6UWszaQ', 'type': 2, 'version': 1}
