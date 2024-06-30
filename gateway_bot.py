import discord
import os

from util.discord_apis import (create_secret_channel, get_role,
                               get_guild_channel_by_name, get_channel_messages)

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
GUILD_ID = os.environ.get("DISCORD_GUILD_ID")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True

client = discord.Client(intents=intents)

everyone_role = get_role(GUILD_ID, "@everyone")
getting_started_channel = get_guild_channel_by_name(GUILD_ID, "getting-started")
messages = get_channel_messages(getting_started_channel['id'])


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')


@client.event
async def on_raw_reaction_add(payload):
    print(payload.emoji)
    if str(payload.message_id) == messages[1]['id']:
        create_secret_channel(GUILD_ID, everyone_role['id'],
                              f"{payload.member.name}-register", [payload.member.id])

# Event handler for when the bot joins a new guild
@client.event
async def on_guild_join(guild):
    guild_info = (
        f"Joined a new guild:\n"
        f"Guild Name: {guild.name}\n"
        f"Guild ID: {guild.id}\n"
        f"Guild Owner: {guild.owner}\n"
        f"Guild Member Count: {guild.member_count}\n"
    )
    print(guild_info)

client.run(TOKEN)
