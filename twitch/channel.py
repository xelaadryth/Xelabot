from copy import deepcopy

import settings
from utils.command_set import CommandSet


class Channel:
    default_settings = {
        'name': None,
        'auto_join': False
    }

    def __init__(self, owner, channel_manager):
        self.owner = owner
        self.channel_settings = deepcopy(self.default_settings)
        self.channel_manager = channel_manager

        self.mod_commands = CommandSet()
        self.commands = CommandSet(exact_match_commands={
            '!requestjoin': self.request_join,
            '!requestleave': self.request_leave
        })

    def send_msg(self, msg):
        """
        Makes the bot send a message in the current channel.
        :param msg: str - The message to send.
        """
        self.channel_manager.bot.send_msg(self.owner, msg)

    def check_commands(self, display_name, msg, is_mod, is_sub):
        """
        Connect to other command lists whose requirements are met.
        :param display_name: str - The display name of the command sender
        :param msg: str - The full message that the user sent that starts with "!"
        :param is_mod: bool - Whether the sender is a mod
        :param is_sub: bool - Whether the sender is a sub
        """
        # Channel owner gets all accesses
        if display_name.lower() == self.owner:
            is_mod = True
            is_sub = True

        if is_mod:
            self.mod_commands.execute_command(display_name, msg)
        else:
            if self.mod_commands.has_command(msg):
                self.channel_manager.bot.send_whisper(display_name, 'That\'s a mod-only command.')

        self.commands.execute_command(display_name, msg)

    def request_join(self, display_name):
        """
        Requests the bot to join their channel.
        :param display_name: str - User requesting the bot to join
        """
        if settings.ENABLE_REQUEST_JOIN:
            self.channel_manager.join_channel(display_name.lower())
            self.send_msg('{} has now joined {}\'s channel.'.format(settings.BOT_NAME, display_name))
        else:
            self.send_msg('This command is disabled for this bot. Ask the broadcaster {} to re-enable it.'.format(
                settings.BROADCASTER_NAME))

    def request_leave(self, display_name):
        """
        Requests the bot to leave their channel.
        :param display_name: str - User requesting the bot to leave
        """
        self.channel_manager.leave_channel(display_name.lower())
        self.send_msg('{} has now left {}\'s channel.'.format(settings.BOT_NAME, display_name))

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
