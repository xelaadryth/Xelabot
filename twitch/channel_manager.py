import json
import os
import settings

from .channel import Channel
import settings


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
        self.load_settings_from_db()
        self.initialized = True

    def load_settings_from_db(self):
        """
        Loads all valid data from database into the ChannelManager.
        """
        # Load up all the existing channel information
        if not os.path.exists(settings.CHANNEL_DATA_PATH):
            os.makedirs(settings.CHANNEL_DATA_PATH)
        for filename in os.listdir(settings.CHANNEL_DATA_PATH):
            with open(os.path.join(settings.CHANNEL_DATA_PATH, filename)) as read_file:
                channel_settings = json.load(read_file)

            default_channel_settings = self.channels[channel_settings['name']].channel_settings
            for key in default_channel_settings:
                if key in channel_settings:
                    default_channel_settings[key] = channel_settings[key]

            self.channels[channel_settings['name']].initialize()

    @staticmethod
    def save_channel_data(channel_name, channel_data):
        """
        Saves a specific channel to persistent storage.
        :param channel_name: str - The owner of the channel you want to save
        :param channel_data: dict - The channel data you are saving
        """
        with open(os.path.join(settings.CHANNEL_DATA_PATH, channel_name + '.txt'), 'w') as channel_file:
            json.dump(channel_data, channel_file, indent=4, sort_keys=True)

    def save_channel(self, channel_name):
        """
        Saves a specific channel to persistent storage.
        :param channel_name: str - The owner of the channel you want to save
        """
        channel_name = channel_name.lower()
        channel_data = self.channels[channel_name].channel_settings

        self.save_channel_data(channel_name, channel_data)

    def add_channel(self, channel_name):
        """
        Adds a new channel to the ChannelManager.
        :param channel_name: str - The owner of the channel you want to add
        """
        channel_name = channel_name.lower()
        self.enable_auto_join(channel_name)

    def join_channel(self, channel_name):
        """
        Joins a new channel and adds it to the ChannelManager.
        :param channel_name: str - The channel you want to join and add
        """
        channel_name = channel_name.lower()
        self.add_channel(channel_name)
        self.bot.join_channel(channel_name)

    def leave_channel(self, channel_name):
        """
        Turns off auto_join in persistent storage. Does not delete stored data.
        :param channel_name: str - The owner of the channel you want to remove
        """
        channel_name = channel_name.lower()
        self.disable_auto_join(channel_name)
        self.bot.leave_channel(channel_name)

    def reset_channel(self, channel_name):
        """
        Resets a channel back to default settings. Loses all stored data forever and irreversibly!
        :param channel_name: str - The owner of the channel whose data you wish to reset
        """
        channel_name = channel_name.lower()
        self.channels.pop(channel_name, None)
        self.add_channel(channel_name)

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
