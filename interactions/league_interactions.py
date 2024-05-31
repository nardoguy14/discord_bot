import uuid
from datetime import datetime

from discord_interactions import InteractionResponseType, InteractionType

from repositories.leagues_repository import LeaguesRepository
from utils import generate_random_emoji

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
                    }
                ]
            }
        }

    async def process_create_league_modal_submit(self, body):
        name = body['data']['components'][0]['components'][0]['value']
        kind = body['data']['components'][1]['components'][0]['value']
        start_date = body['data']['components'][2]['components'][0]['value']
        end_date = body['data']['components'][3]['components'][0]['value']

        await self.leagues_repository.create_league(name, kind,
                                               datetime.strptime(start_date, '%Y-%m-%d'),
                                               datetime.strptime(end_date, '%Y-%m-%d'))
        return {
            'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            'data': {
                'content': f'League `{name}` of kind `{kind}` successfully made!~ {generate_random_emoji()}'
            }
        }

    async def join_league(self, body):
        user_id = body['member']['user']['id']
        user_name = body['member']['user']['username']
        print(f"userid {user_id} username {user_name}")
        league_name = body['data']['options'][0]['value']
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
