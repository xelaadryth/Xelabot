from quests.quest_manager import QuestManager
from twitch.channel import Channel


class QuestChannel(Channel):
    def __init__(self, owner, channel_settings, channel_manager):
        super().__init__(owner, channel_settings, channel_manager)

        self.quest_manager = QuestManager(self)

        self.mod_commands.exact_match_commands.update({
            '!queston': lambda **_: self.channel_manager.enable_quest(self.owner),
            '!questoff': lambda **_: self.channel_manager.disable_quest(self.owner),
            '!questcooldown': lambda **kwargs: self.set_quest_cooldown(kwargs['full_command'], kwargs['display_name'])
        })

    def set_quest_cooldown(self, full_command='', display_name=''):
        try:
            self.channel_manager.set_quest_cooldown(self.owner, int(full_command.split(maxsplit=1)[1]))
        except (IndexError, ValueError):
            self.channel_manager.bot.send_whisper(display_name, 'Invalid usage! Sample usage: !questcooldown 90')

    def check_commands(self, display_name, msg, is_mod, is_sub):
        super().check_commands(display_name, msg, is_mod, is_sub)

        # Check quest commands
        self.quest_manager.commands.execute_command(msg, display_name=display_name)
