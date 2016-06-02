from copy import deepcopy
import json
import os

from .channel import Channel
from utils.logger import log


import settings


class ChannelManager:
    """
    Keeps track of all channels the bot interacts with.
    """
    channel_type = Channel
    default_channel_settings = {
        'name': None,
        'auto_join': False
    }

    # When a channel is missing, create and save it
    class ChannelDict(dict):
        """
        A dictionary that, when indexed at a non-existent channel name, still returns a default channel
        object. All data in this object is transient and does not get saved to persistent storage.
        """
        def __init__(self, channel_manager):
            super().__init__()
            self.channel_manager = channel_manager

        def __missing__(self, channel_name):
            # Ignore casing
            lower_channel_name = channel_name.lower()
            if channel_name != lower_channel_name:
                return self[lower_channel_name]

            channel = self.channel_manager.channel_type(channel_name, self.channel_manager)
            self[channel_name] = channel

            return channel

    # When a channel settings object is missing, create and save it
    class ChannelSettingsDict(dict):
        """
        A dictionary that, when indexed at a non-existent channel name, still returns a default channel
        settings object that can later be saved to persistent storage on edit.
        """
        def __init__(self, channel_manager):
            super().__init__()
            self.channel_manager = channel_manager

        def __missing__(self, channel_name):
            lower_channel_name = channel_name.lower()
            if channel_name != lower_channel_name:
                return self[lower_channel_name]

            channel_data = deepcopy(self.channel_manager.default_channel_settings)
            channel_data['name'] = channel_name
            self[channel_name] = channel_data

            return channel_data

    def __init__(self, bot):
        self.bot = bot
        self.channels = self.ChannelDict(self)
        self.channel_settings = self.ChannelSettingsDict(self)

        self.load_channel_data()

    def load_channel_data(self):
        """
        Loads all valid channel settings data from persistent storage into the ChannelManager.
        """
        # Load up all the existing channel information
        if not os.path.exists(settings.CHANNEL_DATA_PATH):
            os.makedirs(settings.CHANNEL_DATA_PATH)
        for filename in os.listdir(settings.CHANNEL_DATA_PATH):
            with open(os.path.join(settings.CHANNEL_DATA_PATH, filename)) as read_file:
                channel_data = json.load(read_file)

            # 'name' is a required field
            # On initial opening this is empty and just contains default values
            channel_settings = self.channel_settings[channel_data['name']]

            for key in channel_settings:
                if key in channel_data:
                    channel_settings[key] = channel_data[key]

    @staticmethod
    def save_channel_data(channel_name, channel_data):
        """
        Saves a specific channel to persistent storage.
        :param channel_name: str - The owner of the channel you want to save
        :param channel_data: dict - The channel data you are saving
        """
        channel_name = channel_name.lower()
        with open(os.path.join(settings.CHANNEL_DATA_PATH, channel_name + '.txt'), 'w') as channel_file:
            json.dump(channel_data, channel_file, indent=4, sort_keys=True)

    def save_channel(self, channel_name):
        """
        Saves a specific channel to persistent storage.
        :param channel_name: str - The owner of the channel you want to save
        """
        self.save_channel_data(channel_name, self.channel_settings[channel_name])

    def join_channel(self, channel_name):
        """
        Joins a new channel and sets it for auto-join.
        :param channel_name: str - The channel you want to join and add
        """
        self.enable_auto_join(channel_name)
        self.bot.join_channel(channel_name)

    def leave_channel(self, channel_name):
        """
        Leaves a channel and turns off auto_join in persistent storage. Does not delete stored data.
        :param channel_name: str - The owner of the channel you want to remove
        """
        self.disable_auto_join(channel_name)
        self.bot.leave_channel(channel_name)

    def enable_auto_join(self, channel_name):
        """
        Bot will join the given channel on bot startup.
        :param channel_name: str - The owner of the channel who you are changing settings for
        """
        self.channel_settings[channel_name]['auto_join'] = True
        self.save_channel(channel_name)

    def disable_auto_join(self, channel_name):
        """
        Bot will not join the given channel anymore.
        :param channel_name: str - The owner of the channel who you are changing settings for
        """
        self.channel_settings[channel_name]['auto_join'] = False
        self.save_channel(channel_name)

    def join_all_auto_join(self):
        """
        Join all channels that have auto_join enabled.
        """
        for channel_name, channel_data in self.channel_settings.items():
            if channel_data['auto_join']:
                log('Joining channel: {}...'.format(channel_name))
                self.bot.join_channel(channel_name)
