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

export broker_list=$(aws mq list-brokers)
export broker_id=$(echo "$broker_list" | jq -r '.BrokerSummaries[0].BrokerId')
export broker_details=$(aws mq describe-broker --broker-id "$broker_id")
export endpoint=$(echo "$broker_details" | jq -r '.BrokerInstances[0].Endpoints[0]')
export cleaned_endpoint=${endpoint#*://}
export cleaned_endpoint="${cleaned_endpoint%%:*}"
export REDIS_HOST=$cleaned_endpoint

export USING_FAST_API=1
echo "NARDO LOOK HERE"
echo $REDIS_HOST
echo $DISCORD_BOT_PUBLIC_KEY

echo "stopping containers"
# Stop any existing container
sudo docker stop discord_apis || true
sudo docker rm discord_apis || true
sudo docker stop gateway_bot || true
sudo docker rm gateway_bot || true

echo "pulling latest image"
# Pull the latest image
sudo docker pull nardoarevalo14/twitch_leagues_bot:latest

echo "running api container"
sudo docker run  --name discord_apis -p 80:8000 \
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

echo "running gateway container"
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
 nardoarevalo14/twitch_leagues_bot:latest \
 /bin/bash -c 'python gateway_bot.py'

echo "running celery container"
docker run -d --name celery_worker \
 -e POSTGRES_HOST=$POSTGRES_HOST \
 -e POSTGRES_DB=$POSTGRES_DB \
 -e POSTGRES_USER=$POSTGRES_USER \
 -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
 -e DISCORD_GUILD_ID=$DISCORD_GUILD_ID \
 -e DISCORD_APPLICATION_ID=$DISCORD_APPLICATION_ID \
 -e DISCORD_BOT_TOKEN=$DISCORD_BOT_TOKEN \
 -e DISCORD_BOT_PUBLIC_KEY=$DISCORD_BOT_PUBLIC_KEY \
 -e REDIS_HOST=$REDIS_HOST \
 nardoarevalo14/twitch_leagues_bot:latest \
 /bin/bash -c 'aio_celery worker celery_worker:celery'