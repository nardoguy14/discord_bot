from sqlalchemy import select
from domain.matches import Match
from domain.leagues import LeagueUser
from sqlalchemy import select, func, literal_column, and_
from repositories.base_repository import postgres_base_repo


class MatchesRepository():

    async def find_matches(self, ranking, disparity, league_id):
        query = postgres_base_repo.db.select([LeagueUser.user_id, Match.discord_channel_id]
                                     ).select_from(
            LeagueUser.join(Match, LeagueUser.user_id == Match.player_id)
        ).where(and_(func.abs(LeagueUser.ranking - ranking) < disparity,
                             Match.league_id == league_id))

        result = await query.gino.all()
        return result

    async def create_match(self, league_id, player_id, discord_channel_id):
        return await Match.create(player_id=player_id, league_id=league_id, discord_channel_id=discord_channel_id)

    async def get_match(self, match_id):
        return await Match.query.where(Match.id == match_id).gino.first()

    async def delete_match(self, match: Match):
        match = await self.get_match(match.id)
        return await match.delete()