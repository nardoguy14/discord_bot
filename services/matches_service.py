from domain.leagues import User
from domain.matches import Match
from repositories.matches_repository import MatchesRepository
from discord_interactions import InteractionResponseType

from services.user_service import UserService


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