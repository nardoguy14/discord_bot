from domain.leagues import League, LeagueUser
from sqlalchemy import select, func, literal_column, and_

class LeaguesRepository():

    async def create_league(self, name, kind, start_date, end_date, max_plays_per_week, max_disparity):
        return await League.create(name=name, kind=kind, start_date=start_date, end_date=end_date,
                                   max_plays_per_week=max_plays_per_week, max_disparity=max_disparity)

    async def get_league(self, league_name):
        return await League.query.where((League.name == league_name)).gino.all()

    async def join_league(self, user_id, league_id, ranking):
        return await LeagueUser.create(user_id=user_id, league_id=league_id, ranking=ranking)

    async def get_league_users(self, league_id):
        return await LeagueUser.query.where(LeagueUser.league_id == league_id).gino.all()

    async def get_league_users_within_rank(self, ranking, disparity):
        return await LeagueUser.query.where(func.abs(LeagueUser.ranking - ranking) < disparity,).gino.all()

    async def update_league(self, league_name, start_date=None, end_date=None,
                            new_name=None, max_plays=None, max_disparity=None):
        league = (await self.get_league(league_name))[0]
        args = {}
        if start_date is not None:
            args['start_date'] = start_date
        if end_date is not None:
            args['end_date'] = end_date
        if new_name is not None:
            args['name'] = new_name
        if max_plays is not None:
            args['max_plays_per_week'] = int(max_plays)
        if max_disparity is not None:
            args['max_disparity'] = float(max_disparity)
        await league.update(**args).apply()

    async def delete_league(self, league_name):
        league = (await self.get_league(league_name))[0]
        league_users = await self.get_league_users(league.id)
        for league_user in league_users:
            await league_user.delete()
        await league.delete()
