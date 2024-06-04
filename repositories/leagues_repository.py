from domain.leagues import League, LeagueUser


class LeaguesRepository():

    async def create_league(self, name, kind, start_date, end_date, max_plays_per_week):
        return await League.create(name=name, kind=kind, start_date=start_date, end_date=end_date,
                                   max_plays_per_week=max_plays_per_week)

    async def get_league(self, league_name):
        return await League.query.where((League.name == league_name)).gino.all()

    async def join_league(self, user_id, league_id, ranking):
        return await LeagueUser.create(user_id=user_id, league_id=league_id, ranking=ranking)