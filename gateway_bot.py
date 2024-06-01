import discord
import requests
import os

from discord_apis import create_secret_channel
from domain.roles import GUILD_ID, EVERYONE_ROLE_ID

# Define your bot token and webhook URL
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")


# Create a bot instance
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_raw_reaction_add(payload):
    print(payload.emoji)
    if payload.message_id == 1246269791455416380:
        create_secret_channel(GUILD_ID, EVERYONE_ROLE_ID,
                              f"{payload.member.name}-register", [payload.member.id])

client.run(TOKEN)
