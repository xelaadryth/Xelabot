from .commands import Commands
from quests.quest import Quest


class Channel:
    def __init__(self, owner, channel_settings, channel_manager):
        self.owner = owner
        self.channel_manager = channel_manager
        self.channel_settings = channel_settings

        self.mod_commands = Commands(exact_match_commands={
            '!queston': lambda **_: self.channel_manager.enable_quest(self.owner),
            '!questoff': lambda **_: self.channel_manager.disable_quest(self.owner),
            '!questcooldown': lambda **kwargs: self.set_quest_cooldown(kwargs['full_command'], kwargs['display_name'])
        })

        self.quest = Quest(self, self.channel_manager.bot)

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
        # Channel owner gets all accesses
        if display_name.lower() == self.owner:
            is_mod = True
            is_sub = True

        command = msg.split(maxsplit=1)[0]

        if is_mod:
            self.mod_commands.execute_command(command, display_name=display_name, full_command=msg)
        else:
            if command in self.mod_commands.exact_match_commands:
                self.channel_manager.bot.send_whisper(display_name.lower(), 'That\'s a mod-only command.')

        # Check quest commands
        if self.channel_settings['quest_enabled']:
            self.quest.check_commands(display_name.lower(), msg)
        elif msg.lower() == "!quest":
            self.send_msg("Questing is currently disabled. Mods can use !queston to re-enable questing.")

        # TODO: Add back in loyalty commands with https://tmi.twitch.tv/group/user/USERNAME_HERE/chatters
        # Check loyalty commands
        # if msg == "!" + self.channel_settings['loyalty_name']:
        #     if user == self.owner:
        #         self.send_msg("You are the owner of this channel.")
        #     elif user in self.channel_settings['loyalty']:
        #         self.send_msg(user + " has " + str(self.channel_settings['loyalty'][user]) + " " +
        #                       self.channel_settings['loyalty_name'] + ".")
        #     else:
        #         self.send_msg(user + " has 0 " + self.channel_settings['loyalty_name'] + ".")
