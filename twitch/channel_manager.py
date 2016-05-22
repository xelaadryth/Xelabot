import copy
import json
import os
import settings

from .channel import Channel


class ChannelManager:
    """
    Keeps track of all channels the bot interacts with.
    """
    default_settings = {
        'name': None,
        'auto_join': True,
        'quest_enabled': True,
        'quest_cooldown': settings.QUEST_DEFAULT_COOLDOWN
    }

    def __init__(self, bot):
        self.bot = bot
        self.channels = {}

        # Load up all the existing channel information
        if not os.path.exists(settings.CHANNEL_DATA_PATH):
            os.makedirs(settings.CHANNEL_DATA_PATH)
        for filename in os.listdir(settings.CHANNEL_DATA_PATH):
            with open(os.path.join(settings.CHANNEL_DATA_PATH, filename)) as json_data:
                channel_settings = json.load(json_data)

            # Fill missing settings with default settings
            channel_settings_keys = set(channel_settings.keys())
            for key, value in self.default_settings.items():
                if key not in channel_settings_keys:
                    channel_settings[key] = value

            self.channels[channel_settings['name']] = Channel(channel_settings['name'], channel_settings, self)

    def save_channel(self, username):
        """
        Saves a specific channel to persistent storage.
        :param username: str - The owner of the channel you want to save
        """
        channel = self.channels[username]

        with open(os.path.join(
                settings.CHANNEL_DATA_PATH, channel.channel_settings['name'] + '.txt'), 'w') as channel_file:
            json.dump(channel.channel_settings, channel_file)

    def add_channel(self, username):
        """
        Adds a new channel to the ChannelManager.
        :param username: str - The owner of the channel you want to add
        """
        if username not in self.channels:
            channel_settings = copy.deepcopy(ChannelManager.default_settings)
            channel_settings['name'] = username.lower()
            self.channels[username] = Channel(channel_settings['name'], channel_settings, self.bot)
            self.save_channel(username)
        else:
            self.channels[username].enable_auto_join()

    def delete_channel(self, username):
        """
        Turns off auto_join in persistent storage. Does not delete stored data.
        :param username: str - The owner of the channel you want to remove
        """
        if username in self.channels.keys():
            self.disable_auto_join(username)

    def reset_channel(self, username):
        """
        Resets a channel back to default settings. Loses all stored data forever and irreversibly!
        :param username: str - The owner of the channel whose data you wish to reset
        """
        self.channels.pop(username)
        self.add_channel(username)

    def enable_quest(self, channel_name):
        """
        Enables the ability to start quests in the current channel.
        :param channel_name: str - The owner of the channel who you are changing settings for
        """
        channel = self.channels[channel_name]
        if not channel.channel_settings['quest_enabled']:
            channel.channel_settings['quest_enabled'] = True
            self.channels[channel_name].quest.quest_advance()
            self.save_channel(channel_name)
            self.bot.send_msg(channel_name, 'Questing enabled. Type "!quest" to start a quest!')
        else:
            self.bot.send_msg(channel_name, 'Questing already enabled. Type "!quest" to start a quest!')

    def disable_quest(self, channel_name):
        """
        Disables the ability to start quests in the current channel.
        :param channel_name: str - The owner of the channel who you are changing settings for
        """
        if self.channels[channel_name].channel_settings['quest_enabled']:
            self.channels[channel_name].quest.kill_timer()
            self.channels[channel_name].quest.quest_state = 0
            self.channels[channel_name].channel_settings['quest_enabled'] = False
            self.save_channel(channel_name)
            self.bot.send_msg(channel_name, "Questing disabled.")
        else:
            self.bot.send_msg(channel_name, "Questing already disabled.")

    def enable_auto_join(self, channel_name):
        """
        Bot will join the given channel on bot startup.
        :param channel_name: str - The owner of the channel who you are changing settings for
        """
        self.channels[channel_name].channel_settings['auto_join'] = True
        self.save_channel(channel_name)

    def disable_auto_join(self, channel_name):
        """
        Bot will not join the given channel anymore.
        :param channel_name: str - The owner of the channel who you are changing settings for
        """
        self.channels[channel_name].channel_settings['auto_join'] = False
        self.save_channel(channel_name)

    def set_quest_cooldown(self, channel_name, cooldown):
        """
        Set the cooldown for going on quests.
        :param channel_name: str - The owner of the channel who you are changing settings for
        :param cooldown: int - The number of seconds you must wait before going on another quest.
        """
        channel = self.channels[channel_name]
        if cooldown < 5:
            channel.send_msg('Cooldown must be at least 5 seconds.')
            return

        self.channels[channel_name].channel_settings['quest_cooldown'] = cooldown
        self.save_channel(channel_name)

        channel.send_msg('Channel cooldown set to {} seconds.'.format(cooldown))
