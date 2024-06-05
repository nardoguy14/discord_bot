from domain.leagues import League, LeagueUser


class LeaguesRepository():

    async def create_league(self, name, kind, start_date, end_date, max_plays_per_week, max_disparity):
        return await League.create(name=name, kind=kind, start_date=start_date, end_date=end_date,
                                   max_plays_per_week=max_plays_per_week, max_disparity=max_disparity)

    async def get_league(self, league_name):
        return await League.query.where((League.name == league_name)).gino.all()

    async def join_league(self, user_id, league_id, ranking):
        return await LeagueUser.create(user_id=user_id, league_id=league_id, ranking=ranking)

    async def update_league(self, league_name, start_date=None, end_date=None,
                            new_name=None, max_plays=None, max_disparity=None):
        league = await self.get_league(league_name)
        if start_date is not None:
            league.start_date = start_date
        if end_date is not None:
            league.end_date = end_date
        if new_name is not None:
            league.name = new_name
        if max_plays is not None:
            league.max_plays_per_week = max_plays
        if max_disparity is not None:
            league.max_disparity = max_disparity
        league.update().apply()