import discord
import os

from discord_apis import (create_secret_channel, get_role,
                          get_guild_channel_by_name, get_channel_messages)

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
GUILD_ID = os.environ.get("DISCORD_GUILD_ID")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True

client = discord.Client(intents=intents)

everyone_role = get_role(GUILD_ID, "@everyone")
welcome_channel = get_guild_channel_by_name(GUILD_ID, "welcome")
messages = get_channel_messages(welcome_channel['id'])


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')


@client.event
async def on_raw_reaction_add(payload):
    print(payload.emoji)
    if str(payload.message_id) == messages[1]['id']:
        create_secret_channel(GUILD_ID, everyone_role['id'],
                              f"{payload.member.name}-register", [payload.member.id])

client.run(TOKEN)
