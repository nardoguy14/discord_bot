import discord
import os

from discord_apis import create_secret_channel, get_role

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
GUILD_ID = os.environ.get("DISCORD_GUILD_ID")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True

client = discord.Client(intents=intents)

everyone_role = get_role(GUILD_ID, "@everyone")

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_raw_reaction_add(payload):
    print(payload.emoji)
    if payload.message_id == 1246269791455416380:
        create_secret_channel(GUILD_ID, everyone_role['id'],
                              f"{payload.member.name}-register", [payload.member.id])

client.run(TOKEN)
