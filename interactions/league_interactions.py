import uuid
from datetime import datetime
import os

from discord_interactions import InteractionResponseType, InteractionType

from repositories.leagues_repository import LeaguesRepository
from utils import generate_random_emoji
from discord_apis import get_role, create_channel, get_guild_channel_by_name, create_message

GUILD_ID = os.environ.get("DISCORD_GUILD_ID")
EVERYONE_ROLE = get_role(GUILD_ID, "@everyone")
HOMIE_USERS = get_role(GUILD_ID, "HOMIE_USERS")
LEAGUE_CHANNEL = get_guild_channel_by_name(GUILD_ID, "Leagues")
ANNOUNCEMENTS_CHANNEL = get_guild_channel_by_name(GUILD_ID, "announcements")

class LeagueInteractions():
    leagues_repository = LeaguesRepository()

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
        create_channel(GUILD_ID, f"{name}", permissions, parent_id=LEAGUE_CHANNEL['id'])
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
        if body['channel']['parent_id'] != LEAGUE_CHANNEL['id']:
            return {
                'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                'data': {
                    'content': f'Can only join leagues in league channels.'
                }
            }
        user_id = body['member']['user']['id']
        user_name = body['member']['user']['username']
        print(f"userid {user_id} username {user_name}")
        league_name = body['channel']['name']
        league_opt = await self.leagues_repository.get_league(league_name)
        if len(league_opt) > 0:
            await self.leagues_repository.join_league(user_id, league_opt[0].id)
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
