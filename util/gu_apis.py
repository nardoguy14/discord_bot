import requests

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

get_rank("1314618")

get_modes()