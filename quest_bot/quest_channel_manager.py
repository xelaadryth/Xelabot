from copy import deepcopy

from .quest_channel import QuestChannel
import settings
from twitch.channel_manager import ChannelManager


class QuestChannelManager(ChannelManager):
    """
    Keeps track of all channels the quest bot interacts with.
    """
    default_channel_settings = deepcopy(ChannelManager.default_channel_settings)
    default_channel_settings.update({
        'quest_enabled': True,
        'quest_cooldown': settings.QUEST_DEFAULT_COOLDOWN
    })
    channel_type = QuestChannel

    def enable_quest(self, channel_name):
        """
        Enables the ability to start quest in the current channel.
        :param channel_name: str - The owner of the channel who you are changing settings for
        """
        if not self.channel_settings[channel_name]['quest_enabled']:
            self.channel_settings[channel_name]['quest_enabled'] = True
            self.channels[channel_name].quest_manager.enable_questing()
            self.save_channel(channel_name)
            self.bot.send_msg(channel_name, 'Questing enabled. Type "!quest" to start a quest!')
        else:
            self.bot.send_msg(channel_name, 'Questing already enabled. Type "!quest" to start a quest!')

    def disable_quest(self, channel_name):
        """
        Disables the ability to start quest in the current channel.
        :param channel_name: str - The owner of the channel who you are changing settings for
        """
        if self.channel_settings[channel_name]['quest_enabled']:
            self.channels[channel_name].quest_manager.disable_questing()
            self.channel_settings[channel_name]['quest_enabled'] = False
            self.save_channel(channel_name)
            self.bot.send_msg(channel_name, 'Questing disabled.')
        else:
            self.bot.send_msg(channel_name, 'Questing already disabled.')

    def set_quest_cooldown(self, channel_name, cooldown):
        """
        Set the cooldown for going on quest.
        :param channel_name: str - The owner of the channel who you are changing settings for
        :param cooldown: int - The number of seconds you must wait before going on another quest.
        """
        channel = self.channels[channel_name]
        if cooldown < 5:
            channel.send_msg('Cooldown must be at least 5 seconds.')
            return

        self.channel_settings[channel_name]['quest_cooldown'] = cooldown
        self.save_channel(channel_name)

        channel.send_msg('Channel cooldown set to {} seconds.'.format(cooldown))

        quest_timer = channel.quest_manager.quest_timer
        if quest_timer and cooldown < quest_timer.remaining():
            quest_timer.set(cooldown)
