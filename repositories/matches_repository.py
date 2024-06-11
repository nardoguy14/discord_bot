from typing import Optional

from sqlalchemy import select
from domain.matches import Match
from domain.leagues import LeagueUser
from sqlalchemy import select, func, literal_column, and_
from repositories.base_repository import postgres_base_repo


class MatchesRepository():

    async def find_matches(self, league_id, player_id_2, user_ids) -> Optional[Match]:
        async with postgres_base_repo.db.transaction():
            query = Match.query.where(
                        and_(
                            Match.player_id_1.in_(user_ids),
                            Match.league_id == league_id,
                            Match.player_id_2.is_(None)
                        )
                    )
            match = await query.gino.first()
            if match:
                await match.update(player_id_2=player_id_2).apply()
                return match
            else:
                return None

    async def create_match(self, league_id, player_id, discord_channel_id):
        return await Match.create(player_id_1=player_id, league_id=league_id, discord_channel_id=discord_channel_id)

    async def get_match(self, match_id):
        return await Match.query.where(Match.id == match_id).gino.first()

    async def get_match_by_discord_id(self, discord_channel_id):
        return await Match.query.where(Match.discord_channel_id == discord_channel_id).gino.first()

    async def delete_match(self, match: Match):
        match = await self.get_match(match.id)
        return await match.delete()

    async def set_ready(self, match: Match, player_id, status=True):
        current_match = await self.get_match(match.id)
        if current_match.player_id_1 == player_id:
            await current_match.update(ready_up_1=status).apply()
        else:
            await current_match.update(ready_up_2=status).apply()
