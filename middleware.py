import json
import os
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from discord_interactions import verify_key_decorator, verify_key, InteractionType, InteractionResponseType
from starlette.middleware.base import BaseHTTPMiddleware

PUBLIC_KEY = os.environ.get("DISCORD_BOT_PUBLIC_KEY")


class DiscordMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, req: Request, call_next):

        print("Processing request:", req.url)

        b = await req.body()
        body = json.loads(b.decode('utf-8'))
        signature = req.headers.get('X-Signature-Ed25519')
        timestamp = req.headers.get('X-Signature-Timestamp')
        skip_check = req.headers.get('X-Skip-Check', False)
        print(f"sig: {signature} timestamp: {timestamp}")
        print(f"body: {body}")

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