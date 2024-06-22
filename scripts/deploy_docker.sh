#!/bin/bash

POSTGRES_HOST=$(aws rds describe-db-instances --db-instance-identifier discord-bot-rds-db --query "DBInstances[0].Endpoint.Address")
POSTGRES_HOST=$(echo ${POSTGRES_HOST//\"/})
POSTGRES_DB=tempo
POSTGRES_USER=admin
POSTGRES_PASSWORD=$(aws ssm get-parameter --name /myapp/POSTGRES_PASSWORD --query "Parameter.Value" --output text)

DISCORD_GUILD_ID=$(aws ssm get-parameter --name /myapp/DISCORD_GUILD_ID --query "Parameter.Value" --output text)
DISCORD_APPLICATION_ID=$(aws ssm get-parameter --name /myapp/DISCORD_APPLICATION_ID --query "Parameter.Value" --output text)
DISCORD_BOT_TOKEN=$(aws ssm get-parameter --name /myapp/DISCORD_BOT_TOKEN --query "Parameter.Value" --output text)
DISCORD_BOT_PUBLIC_KEY=$(aws ssm get-parameter --name /myapp/DISCORD_BOT_PUBLIC_KEY --query "Parameter.Value" --output text)

REDIS_HOST=docker.for.mac.localhost
USING_FAST_API=1


# Stop any existing container
docker stop discord_apis || true
docker rm discord_apis || true

# Pull the latest image
docker pull nardoarevalo14/twitch_leagues_bot:latest

pip install --no-cache-dir -r requirements.txt
alembic upgrade head

# Run the container
docker run -d --name discord_apis -p 8000:8000 \
 -e POSTGRES_HOST=$POSTGRES_HOST \
 -e POSTGRES_DB=$POSTGRES_DB \
 -e POSTGRES_USER=$POSTGRES_USER \
 -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
 -e DISCORD_GUILD_ID=$DISCORD_GUILD_ID \
 -e DISCORD_APPLICATION_ID=$DISCORD_APPLICATION_ID \
 -e DISCORD_BOT_TOKEN=$DISCORD_BOT_TOKEN \
 -e DISCORD_BOT_PUBLIC_KEY=$DISCORD_BOT_PUBLIC_KEY \
 -e REDIS_HOST=$REDIS_HOST \
 -e USING_FAST_API=$USING_FAST_API \
 nardoarevalo14/twitch_leagues_bot:latest

docker run -d --name gateway_bot -p 8000:8000 \
 -e POSTGRES_HOST=$POSTGRES_HOST \
 -e POSTGRES_DB=$POSTGRES_DB \
 -e POSTGRES_USER=$POSTGRES_USER \
 -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
 -e DISCORD_GUILD_ID=$DISCORD_GUILD_ID \
 -e DISCORD_APPLICATION_ID=$DISCORD_APPLICATION_ID \
 -e DISCORD_BOT_TOKEN=$DISCORD_BOT_TOKEN \
 -e DISCORD_BOT_PUBLIC_KEY=$DISCORD_BOT_PUBLIC_KEY \
 -e REDIS_HOST=$REDIS_HOST \
 -e USING_FAST_API=$USING_FAST_API \
 nardoarevalo14/twitch_leagues_bot:latest \
 /bin/bash -c 'python gateway_bot.py'

docker run -d --name celery_worker -p 8000:8000 \
 -e POSTGRES_HOST=$POSTGRES_HOST \
 -e POSTGRES_DB=$POSTGRES_DB \
 -e POSTGRES_USER=$POSTGRES_USER \
 -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
 -e DISCORD_GUILD_ID=$DISCORD_GUILD_ID \
 -e DISCORD_APPLICATION_ID=$DISCORD_APPLICATION_ID \
 -e DISCORD_BOT_TOKEN=$DISCORD_BOT_TOKEN \
 -e DISCORD_BOT_PUBLIC_KEY=$DISCORD_BOT_PUBLIC_KEY \
 -e REDIS_HOST=$REDIS_HOST \
 -e USING_FAST_API=$USING_FAST_API \
 nardoarevalo14/twitch_leagues_bot:latest \
 /bin/bash -c 'aio_celery worker celery_worker:celery'