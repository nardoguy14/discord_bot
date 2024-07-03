#!/bin/bash

export POSTGRES_HOST=$(aws rds describe-db-instances --db-instance-identifier discord-bot-rds-db --query "DBInstances[0].Endpoint.Address")
export POSTGRES_HOST=$(echo ${POSTGRES_HOST//\"/})
export POSTGRES_DB=tempo
export POSTGRES_USER=adminwhatup
export POSTGRES_PASSWORD=$POSTGRES_PASSWORD # set by git actions to cloudformation to userdata in ec2

export DISCORD_GUILD_ID=$(aws ssm get-parameter --name /MyApp/DISCORD_GUILD_ID --query "Parameter.Value" --with-decryption --output text)
export DISCORD_APPLICATION_ID=$(aws ssm get-parameter --name /MyApp/DISCORD_APPLICATION_ID --query "Parameter.Value" --with-decryption --output text)
export DISCORD_BOT_TOKEN=$(aws ssm get-parameter --name /MyApp/DISCORD_BOT_TOKEN --query "Parameter.Value" --with-decryption --output text)
export DISCORD_BOT_PUBLIC_KEY=$(aws ssm get-parameter --name /MyApp/DISCORD_BOT_PUBLIC_KEY --query "Parameter.Value" --with-decryption  --output text)

export REDIS_HOST=rabbitmq

export USING_FAST_API=1

sudo docker network create my-network || true

echo "stopping containers"
# Stop any existing container
sudo docker stop discord_apis || true
sudo docker rm discord_apis || true
sudo docker stop gateway_bot || true
sudo docker rm gateway_bot || true
sudo docker stop rabbitmq || true
sudo docker rm rabbitmq || true
sudo docker stop celery_worker || true
sudo docker rm celery_worker || true
docker rmi $(docker images -q)


echo "pulling latest image"
# Pull the latest image
sudo docker pull nardoarevalo14/twitch_leagues_bot:latest
sudo docker pull rabbitmq:management || true

echo "running rabbitmq"
sudo docker run -d --name rabbitmq --network my-network -p 5672:5672 -p 15672:15672 rabbitmq:management || true

echo "running api container"
sudo docker run -d --name discord_apis -p 80:8000 \
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
 --network my-network \
 nardoarevalo14/twitch_leagues_bot:latest

echo "running gateway container"
sudo docker run -d --name gateway_bot -p 8000:8000 \
 -e POSTGRES_HOST=$POSTGRES_HOST \
 -e POSTGRES_DB=$POSTGRES_DB \
 -e POSTGRES_USER=$POSTGRES_USER \
 -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
 -e DISCORD_GUILD_ID=$DISCORD_GUILD_ID \
 -e DISCORD_APPLICATION_ID=$DISCORD_APPLICATION_ID \
 -e DISCORD_BOT_TOKEN=$DISCORD_BOT_TOKEN \
 -e DISCORD_BOT_PUBLIC_KEY=$DISCORD_BOT_PUBLIC_KEY \
 -e REDIS_HOST=$REDIS_HOST \
 --network my-network \
 nardoarevalo14/twitch_leagues_bot:latest \
 /bin/bash -c 'python gateway_bot.py'

echo "running celery container"
sudo docker run -d --name celery_worker \
 -e POSTGRES_HOST=$POSTGRES_HOST \
 -e POSTGRES_DB=$POSTGRES_DB \
 -e POSTGRES_USER=$POSTGRES_USER \
 -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
 -e DISCORD_GUILD_ID=$DISCORD_GUILD_ID \
 -e DISCORD_APPLICATION_ID=$DISCORD_APPLICATION_ID \
 -e DISCORD_BOT_TOKEN=$DISCORD_BOT_TOKEN \
 -e DISCORD_BOT_PUBLIC_KEY=$DISCORD_BOT_PUBLIC_KEY \
 -e REDIS_HOST=$REDIS_HOST \
 --network my-network \
 nardoarevalo14/twitch_leagues_bot:latest \
 /bin/bash -c 'aio_celery worker celery_worker:celery'
