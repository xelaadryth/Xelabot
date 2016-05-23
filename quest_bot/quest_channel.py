from quests.quest_manager import QuestManager
from twitch.channel import Channel


class QuestChannel(Channel):
    def __init__(self, owner, channel_settings, channel_manager):
        super().__init__(owner, channel_settings, channel_manager)

        self.mod_commands.exact_match_commands.update({
            '!queston': lambda **_: self.channel_manager.enable_quest(self.owner),
            '!questoff': lambda **_: self.channel_manager.disable_quest(self.owner),
            '!questcooldown': lambda **kwargs: self.set_quest_cooldown(kwargs['full_command'], kwargs['display_name'])
        })

        self.quest_manager = QuestManager(self, self.channel_manager.bot)

    def send_msg(self, msg):
        """
        Makes the bot send a message in the current channel.
        :param msg: str - The message to send.
        """
        self.channel_manager.bot.send_msg(self.owner, msg)

    def set_quest_cooldown(self, full_command='', display_name=''):
        try:
            self.channel_manager.set_quest_cooldown(self.owner, int(full_command.split(maxsplit=1)[1]))
        except (IndexError, ValueError):
            self.channel_manager.bot.send_whisper(display_name, 'Invalid usage! Sample usage: !questcooldown 90')

    def check_commands(self, display_name, msg, is_mod, is_sub):
        super().check_commands(display_name, msg, is_mod, is_sub)

        # TODO: Move this into quest_manager
        # Check quest commands
        if self.channel_settings['quest_enabled']:
            self.quest_manager.check_commands(display_name.lower(), msg)
        elif msg.lower() == "!quest":
            self.send_msg("Questing is currently disabled. Mods can use !queston to re-enable questing.")
