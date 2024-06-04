from util.discord_apis import delete_channel, get_guild_channels


class LeagueService():

    def delete_league(self, guild_id, league_name):
        channels = get_guild_channels(guild_id)
        parents_to_children = {}
        category_channel = None
        for channel in channels:
            if channel['parent_id'] is not None:
                if channel['parent_id'] in parents_to_children:
                    parents_to_children[channel['parent_id']].append(channel)
                else:
                    parents_to_children[channel['parent_id']] = [channel]
            if league_name in channel['name']:
                category_channel = channel
        for subchannel in parents_to_children[category_channel['id']]:
            delete_channel(subchannel['id'])
        delete_channel(category_channel['id'])
