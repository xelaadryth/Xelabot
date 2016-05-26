import json
import os
import settings

from .channel import Channel


class ChannelManager:
    """
    Keeps track of all channels the bot interacts with.
    """
    channel_type = Channel

    # When a channel is missing, create and save it
    class ChannelDict(dict):
        """
        A dictionary that, when indexed at a non-existent channel name, still returns a default channel
        object that is also saved to persistent storage.
        """
        def __init__(self, channel_manager):
            super().__init__()
            self.channel_manager = channel_manager

        def __missing__(self, key):
            channel = self.channel_manager.channel_type(key, self.channel_manager)
            channel.channel_settings['name'] = key
            self[key] = channel
            if self.channel_manager.initialized:
                self.channel_manager.save_channel_data(key, channel.channel_settings)
            return channel

    def __init__(self, bot):
        self.bot = bot
        self.channels = self.ChannelDict(self)
        self.initialized = False

        # Load up all the existing channel information
        if not os.path.exists(settings.CHANNEL_DATA_PATH):
            os.makedirs(settings.CHANNEL_DATA_PATH)
        for filename in os.listdir(settings.CHANNEL_DATA_PATH):
            with open(os.path.join(settings.CHANNEL_DATA_PATH, filename)) as read_file:
                channel_settings = json.load(read_file)

            self.channels[channel_settings['name']].channel_settings.update(channel_settings)

        self.initialized = True

    @staticmethod
    def save_channel_data(username, data):
        """
        Saves a specific channel to persistent storage.
        :param username: str - The owner of the channel you want to save
        :param data: dict - The channel data you are saving
        """
        with open(os.path.join(settings.CHANNEL_DATA_PATH, username + '.txt'), 'w') as channel_file:
            json.dump(data, channel_file, indent=4, sort_keys=True)

    def save_channel(self, username):
        """
        Saves a specific channel to persistent storage.
        :param username: str - The owner of the channel you want to save
        """
        username = username.lower()
        channel_data = self.channels[username].channel_settings

        self.save_channel_data(username, channel_data)

    def add_channel(self, username):
        """
        Adds a new channel to the ChannelManager.
        :param username: str - The owner of the channel you want to add
        """
        username = username.lower()
        self.enable_auto_join(username)

    def join_channel(self, username):
        """
        Joins a new channel and adds it to the ChannelManager.
        :param username: str - The channel you want to join and add
        """
        username = username.lower()
        self.add_channel(username)
        self.bot.join_channel(username)

    def leave_channel(self, username):
        """
        Turns off auto_join in persistent storage. Does not delete stored data.
        :param username: str - The owner of the channel you want to remove
        """
        username = username.lower()
        self.disable_auto_join(username)
        self.bot.leave_channel(username)

    def reset_channel(self, username):
        """
        Resets a channel back to default settings. Loses all stored data forever and irreversibly!
        :param username: str - The owner of the channel whose data you wish to reset
        """
        username = username.lower()
        self.channels.pop(username, None)
        self.add_channel(username)

    def enable_auto_join(self, channel_name):
        """
        Bot will join the given channel on bot startup.
        :param channel_name: str - The owner of the channel who you are changing settings for
        """
        channel_name = channel_name.lower()
        self.channels[channel_name].channel_settings['auto_join'] = True
        self.save_channel(channel_name)

    def disable_auto_join(self, channel_name):
        """
        Bot will not join the given channel anymore.
        :param channel_name: str - The owner of the channel who you are changing settings for
        """
        channel_name = channel_name.lower()
        self.channels[channel_name].channel_settings['auto_join'] = False
        self.save_channel(channel_name)
