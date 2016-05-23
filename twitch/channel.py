from utils.commands import Commands


class Channel:
    def __init__(self, owner, channel_settings, channel_manager):
        self.owner = owner
        self.channel_settings = channel_settings
        self.channel_manager = channel_manager

        self.mod_commands = Commands()

    def send_msg(self, msg):
        """
        Makes the bot send a message in the current channel.
        :param msg: str - The message to send.
        """
        self.channel_manager.bot.send_msg(self.owner, msg)

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
