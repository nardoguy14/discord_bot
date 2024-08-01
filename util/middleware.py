import json
import os
import pprint

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from discord_interactions import verify_key_decorator, verify_key, InteractionType, InteractionResponseType
from starlette.middleware.base import BaseHTTPMiddleware
from functools import wraps

from domain.roles import Role
from repositories.user_repository import User, UserRepository

user_repository = UserRepository()


PUBLIC_KEY = os.environ.get("DISCORD_BOT_PUBLIC_KEY")


class DiscordMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, req: Request, call_next):

        print("Processing request:", req.url)

        b = await req.body()
        print(f"body {b}")
        s = b.decode('utf-8')
        if s == '':
            response = await call_next(req)
            return response
        body = json.loads(s)
        signature = req.headers.get('X-Signature-Ed25519')
        timestamp = req.headers.get('X-Signature-Timestamp')
        skip_check = req.headers.get('X-Skip-Check', False)
        print(f"sig: {signature} timestamp: {timestamp}")
        pprint.pprint(body)

        if not bool(int(skip_check)):

            if signature is None or timestamp is None or not verify_key(b, signature, timestamp, PUBLIC_KEY):
                print("bad bad")
                return PlainTextResponse(status_code=401, content='Bad request signature')

            if body['type'] == InteractionType.PING:
                result = {
                    'type': InteractionResponseType.PONG
                }
                resp = JSONResponse(content=result)
                return resp

        response = await call_next(req)
        return response


def check_role():
    def decorator(func):
        @wraps(func)
        async def wrapper(req: Request, *args, **kwargs):
            b = await req.body()
            body = json.loads(b.decode('utf-8'))
            role_ids = body['member']['roles']

            role_names = []
            for role_id in role_ids:
                role = await user_repository.get_role_by_id(role_id)
                if role:
                    role_names.append(role.name)
            pprint.pprint(role_names)
            pprint.pprint(body)

            if is_modal_submit(body) and "create_league" in body['data']['custom_id']:
                command_name = "create-league"
            elif is_command_type(body):
                command_name = body['data']['name']
            elif is_component_response(body):
                command_name = body['data']['custom_id']
            else:
                command_name = None
            allowed_roles = get_required_role(command_name)
            pprint.pprint(allowed_roles)

            has_allowed_role = set(role_names).intersection(set(allowed_roles))
            if has_allowed_role or role_names == allowed_roles or allowed_roles == []:
                print("WEEEEE")
                # If authenticated, call the original function
                return await func(req, *args, **kwargs)
            else:
                return JSONResponse(status_code=200, content={
                    'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    'data': {
                        'content': f'Sorry you don\'t have permission to do this!'
                    }
                })

        return wrapper

    return decorator


def get_required_role(command_name):
    commands = {
        "register": [],
        "create-league": [Role.HOMIE_ADMIN.name],
        "join-league": [Role.HOMIE_USERS.name],
        "submit-deck": [Role.HOMIE_USERS.name],
        "READY_UP": [Role.HOMIE_USERS.name],
        "DONT_READY_UP": [Role.HOMIE_USERS.name],
    }
    return commands.get(command_name, [])


def is_modal_submit(body):
    return body['type'] == 5

def is_command_type(body):
    return body['type'] == InteractionType.APPLICATION_COMMAND

def is_component_response(body):
    return body['type'] == InteractionType.MESSAGE_COMPONENT