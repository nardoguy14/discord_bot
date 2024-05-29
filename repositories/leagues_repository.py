from domain.leagues import League


class LeaguesRepository():

    async def create_league(self, name, kind, start_date, end_date):
        result = await League.create(name=name, kind=kind, start_date=start_date, end_date=end_date)
        return result