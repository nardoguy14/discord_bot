import requests

from domain.leagues import User

BASE_HOST = "https://api.godsunchained.com/v0"


def get_rank(user_id):
    params = {
        'user_id': user_id,
    }
    endpoint = "/rank"
    response = requests.get(BASE_HOST + endpoint, params=params)
    print(response.text)
    return response.json()


def get_modes():
    endpoint = "/mode"
    response = requests.get(BASE_HOST + endpoint)
    print(response.text)
    return response.json()


def get_user_rank(user: User):
    ranking = get_rank(user.gu_user_id)
    for rank in ranking['records']:
        if rank['game_mode'] == 13:
            return rank["rating"]/100.0
