import os

from domain.matches import Match
from repositories.matches_repository import MatchesRepository
from discord_interactions import InteractionResponseType

from services.user_service import UserService
from util.discord_apis import get_guild_channel_by_name, create_message

GUILD_ID = os.environ.get("DISCORD_GUILD_ID")


class MatchesService:

    matches_repository = MatchesRepository()
    users_service = UserService()

    async def set_ready_up_status(self, discord_channel_id, player_id):

        match: Match = await self.matches_repository.get_match_by_discord_id(discord_channel_id)
        await self.matches_repository.set_ready(match, player_id)

        result = {
            'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            'data': {
                'content': 'Ready up!',
                'components': [
                            {
                                "type": 1,
                                "components": [
                                    {
                                        "type": 2,
                                        "label": "✅",
                                        "style": 1,
                                        "custom_id": "READY_UP"
                                    },
                                    {
                                        "type": 2,
                                        "label": "❌",
                                        "style": 1,
                                        "custom_id": "DONT_READY_UP"
                                    }
                                ]

                            }


                ]
            }
        }

        already_ready_uped = {
            'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            'data': {
                'content': 'Youre already readied up! Hold on!'
            }
        }

        if match.player_id_1 == player_id:
            if match.ready_up_1 is True:
                return already_ready_uped
            else:
                return result
        elif match.player_id_2 == player_id:
            if match.ready_up_2 is True:
                return already_ready_uped
            else:
                return result

    async def react_to_ready_up(self, body):
        player_id = body['member']['user']['id']
        decision = body['data']['custom_id']
        discord_user_id = body['member']['user']['id']
        channel_id = body['channel']['id']
        match: Match = await self.matches_repository.get_match_by_discord_id(channel_id)
        already_ready_uped = {
            'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            'data': {
                'content': 'No need for you to click! You sent the ready up! Hold on!'
            }
        }
        result = {
            'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            'data': {
                'content': 'yayyy everyones ready'
            }
        }
        if match.player_id_1 == player_id:
            if match.ready_up_1 is True:
                return already_ready_uped
            else:
                await self.matches_repository.set_ready(match, player_id)
                return result
        elif match.player_id_2 == player_id:
            if match.ready_up_2 is True:
                return already_ready_uped
            else:
                await self.matches_repository.set_ready(match, player_id)
                return result

    async def wait_for_decks_and_wrap_up_game(self, body):
        from celery_worker import celery, ask_for_decks
        async with celery.setup():
            channel_id = body['channel']['id']
            await ask_for_decks.delay(channel_id)
        return {
            'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            'data': {
                'content': ''
            }
        }

    async def save_deck(self, discord_channel_id, player_id, deck_code):
        await self.matches_repository.set_deck(discord_channel_id, player_id, deck_code)
        return {
            'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            'data': {
                'content': 'Deck saved!'
            }
        }

    async def dispute_modal(self, body):
        return {
            "type": 9,  # MODAL
            "data": {
                "custom_id": "dispute_modal",
                "title": "Dispute a Match",
                "components": [
                    {
                        "type": 1,
                        "components": [
                            {
                                "type": 4,
                                "custom_id": "video_url",
                                "label": "Video Url",
                                "style": 1,  # SHORT
                                "required": False
                            },
                        ]
                    },
                    {
                        "type": 1,
                        "components": [
                            {
                                "type": 4,
                                "custom_id": "image_url",
                                "label": "Image Url",
                                "style": 1,  # SHORT
                                "required": False
                            },
                        ]
                    },
                    {
                        "type": 1,
                        "components": [
                            {
                                "type": 4,
                                "custom_id": "error_description",
                                "label": "What went wrong?",
                                "style": 2  # SHORT
                            },
                        ]
                    }
                ]
            }
        }

    async def dispute_match(self, body):
        if 'matchmaking-' not in body['channel']['name']:
            return {
                'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                'data': {
                    'content': f'Can only execute this in `matchmaking` channel.'
                }
            }
        video_url = body['data']['components'][0]['components'][0]['value']
        image_url = body['data']['components'][1]['components'][0]['value']
        error = body['data']['components'][2]['components'][0]['value']
        match = await self.matches_repository.get_match_by_discord_id(body['channel']['id'])
        member = body['member']['user']['id']
        disputes_channel = get_guild_channel_by_name(GUILD_ID, "disputes")
        create_message(disputes_channel['id'],
                       "**New Dispute**\n\n"
                       f"   Player disputing: `{member}`\n"
                       f"   Match Id: `{match.id}`\n"
                       f"   Discord_channel_id: `{body['channel']['id']}`\n"
                       f"   Video_url: `{video_url} `\n"
                       f"   Image_url: `{image_url} `\n"
                       f"   Error: `{error}`\n"
                       )
        print("weeeeee")
        print(body)
        return {
            'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            'data': {
                'content': '🚨Dispute filed!🚨'
            }
        }
