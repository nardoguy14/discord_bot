from sqlalchemy import select
from domain.matches import Match
from domain.leagues import LeagueUser
from sqlalchemy import select, func, literal_column
from repositories.base_repository import postgres_base_repo

class MatchesRepository():

    async def find_matches(self, ranking, disparity):
        query = (LeagueUser.join(Match, LeagueUser.user_id == Match.player_id)
                 .select()
                 .where(func.abs(LeagueUser.ranking - ranking) < disparity))

        result = await query.gino.all()
        return result


# import asyncio
# loop = asyncio.get_event_loop()
#
#
# async def main():
#     await postgres_base_repo.connect()
#     x = MatchesRepository()
#     print("hiiiiii")
#     result = await x.find_matches(10.0, 10)
#     print(result)
#
# loop.run_until_complete(main())