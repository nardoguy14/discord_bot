from domain.leagues import User
from domain.matches import Match
from repositories.matches_repository import MatchesRepository
from discord_interactions import InteractionResponseType

from services.user_service import UserService
from util.gu_apis import get_matches

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

    async def handle_finished_game(self, body):
        discord_channel_id = body['channel']['id']
        match = await self.matches_repository.get_match_by_discord_id(discord_channel_id)
        player_1: User = await self.users_service.get_user_by_discord_id(match.player_id_1)
        player_2: User = await self.users_service.get_user_by_discord_id(match.player_id_2)
        player_1_matches = get_matches(player_1.gu_user_id)

        league_user_1 = await self.users_service.get_league_user(player_1.discord_id, match.league_id)
        league_user_2 = await self.users_service.get_league_user(player_2.discord_id, match.league_id)

        latest_match_1 = player_1_matches['records'][0]

        player_1_won = False
        player_2_won = False
        if player_1.gu_user_id == str(latest_match_1['player_won']): # and \
            #player_2.gu_user_id == latest_match_1['player_lost']:
            print('player 1 won')
            player_1_won = True
        elif player_1.gu_user_id == str(latest_match_1['player_lost']): # and \
            # player_2.gu_user_id == latest_match_1['player_won']:
            print('player 2 won')
            player_2_won = True

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
        elif league_user_2 < league_user_1.ranking and player_2_won:
            change_in_elo_winner = (abs(league_user_1.ranking - league_user_2.ranking)/ (0.75 + abs(league_user_1.ranking - league_user_2.ranking)))
            change_in_elo_loser = (abs(league_user_1.ranking - league_user_2.ranking)/ (1.0 + abs(league_user_1.ranking - league_user_2.ranking)))
            player_2_new_elo = league_user_2.ranking + change_in_elo_winner
            player_1_new_elo = league_user_1.ranking - change_in_elo_loser

        await self.users_service.update_league_user(league_user_1, {'ranking': player_1_new_elo})
        await self.users_service.update_league_user(league_user_2, {'ranking': player_2_new_elo})

        winner = None
        if player_1_won:
            winner = player_1.gu_user_name
        else:
            winner = player_2.gu_user_name

        return {
            'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            'data': {
                'content': 'Game is set. \n'
                           f'Player: {winner} won.🎉🎊🥳\n'
                           'New elo scores are:\n'
                           f'    Player1 {player_1.gu_user_name}: {player_1_new_elo}\n'
                           f'    Player2 {player_2.gu_user_name}: {player_2_new_elo}'
            }
        }
