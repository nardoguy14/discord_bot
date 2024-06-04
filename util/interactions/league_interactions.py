import uuid
from datetime import datetime
import os

from discord_interactions import InteractionResponseType

from domain.leagues import User
from repositories.leagues_repository import LeaguesRepository
from services.user_service import UserService
from util.gu_apis import get_rank
from utils import generate_random_emoji
from util.discord_apis import get_role, create_channel, get_guild_channel_by_name, create_message, get_guild_channel

GUILD_ID = os.environ.get("DISCORD_GUILD_ID")
EVERYONE_ROLE = get_role(GUILD_ID, "@everyone")
HOMIE_USERS = get_role(GUILD_ID, "HOMIE_USERS")
ANNOUNCEMENTS_CHANNEL = get_guild_channel_by_name(GUILD_ID, "announcements")

class LeagueInteractions():
    leagues_repository = LeaguesRepository()
    user_service = UserService()
    def create_league_interaction(self):
        return {
            "type": InteractionResponseType.MODAL,
            "data": {
                "custom_id": f"create_league_{uuid.uuid4().hex}",
                "title": "Make a New League",
                "components": [
                    {
                        "type": 1,
                        "components": [{
                            "type": 4,
                            "custom_id": "name",
                            "label": "Name",
                            "style": 1,
                            "min_length": 1,
                            "max_length": 200,
                            "placeholder": "Cards Galore League",
                            "required": True
                        }]
                    },
                    {
                        "type": 1,
                        "components": [{
                            "type": 4,
                            "custom_id": "kind",
                            "label": "League Kind",
                            "style": 1,
                            "min_length": 1,
                            "max_length": 200,
                            "placeholder": "Yugi MTG GU Poke!",
                            "required": True
                        }]
                    },
                    {
                        "type": 1,
                        "components": [{
                            "type": 4,
                            "custom_id": "start_date",
                            "label": "Start Date",
                            "style": 1,
                            "min_length": 1,
                            "max_length": 200,
                            "placeholder": "YYYY-MM-DD",
                            "required": True
                        }]
                    },
                    {
                        "type": 1,
                        "components": [{
                            "type": 4,
                            "custom_id": "end_date",
                            "label": "End Date",
                            "style": 1,
                            "min_length": 1,
                            "max_length": 200,
                            "placeholder": "YYYY-MM-DD",
                            "required": True
                        }]
                    },
                    {
                        "type": 1,
                        "components": [{
                            "type": 4,
                            "custom_id": "max_plays_per_weeks",
                            "label": "Max Plays Per Week",
                            "style": 1,
                            "min_length": 1,
                            "max_length": 200,
                            "placeholder": "Number Value",
                            "required": True
                        }]
                    }
                ]
            }
        }

    async def process_create_league_modal_submit(self, body):
        name = body['data']['components'][0]['components'][0]['value']
        kind = body['data']['components'][1]['components'][0]['value']
        start_date = body['data']['components'][2]['components'][0]['value']
        end_date = body['data']['components'][3]['components'][0]['value']
        max_plays_per_week = body['data']['components'][4]['components'][0]['value']
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
                                                int(max_plays_per_week))
        return {
            'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            'data': {
                'content': f'League `{name}` of kind `{kind}` successfully made!~ {generate_random_emoji()}'
            }
        }

    async def join_league(self, body):
        parent_channel = get_guild_channel(GUILD_ID, body['channel']['parent_id'])
        if body['channel']['name'] != 'general-chat' and "league" not in parent_channel['name']:
            return {
                'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                'data': {
                    'content': f'Can only join leagues in `general-chat` channels within a league category.'
                }
            }
        user_id = body['member']['user']['id']
        user_name = body['member']['user']['username']
        print(f"userid {user_id} username {user_name}")
        league_name = body['channel']['name']
        league_opt = await self.leagues_repository.get_league(league_name)
        user: User = await self.user_service.get_user_by_discord_id(user_id)
        if len(league_opt) > 0:
            ranking = get_rank(user.gu_user_id)
            direct_challenge_ranking = None
            for rank in ranking['records']:
                if rank['game_mode'] == 6:
                    direct_challenge_ranking = rank["rank_level"]
                    break
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
