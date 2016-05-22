from quests.quest import Quest


class Channel:
    def __init__(self, owner, channel_settings, bot):
        self.owner = owner
        self.bot = bot

        self.mods = {owner}

        self.channel_settings = channel_settings

        self.quest = Quest(self, bot)

        self.viewers = set()

    def send_msg(self, msg):
        """
        Makes the bot send a message in the current channel.
        :param msg: str - The message to send.
        """
        self.bot.send_msg(self.owner, msg)

    # TODO: Remove this
    def check_commands(self, user, original_msg):
        msg = original_msg.lower()
        if msg[0] == '!':
            # Check quest commands
            if self.channel_settings['quest_enabled']:
                self.quest.check_commands(user, original_msg)
            elif original_msg.lower() == "!quest":
                self.send_msg("Questing is currently disabled. Mods can use !queston to re-enable questing.")

            # Check loyalty commands
            # if msg == "!" + self.channel_settings['loyalty_name']:
            #     if user == self.owner:
            #         self.send_msg("You are the owner of this channel.")
            #     elif user in self.channel_settings['loyalty']:
            #         self.send_msg(user + " has " + str(self.channel_settings['loyalty'][user]) + " " +
            #                       self.channel_settings['loyalty_name'] + ".")
            #     else:
            #         self.send_msg(user + " has 0 " + self.channel_settings['loyalty_name'] + ".")

    def add_mod(self, username):
        """
        Marks a user as a mod in the channel.
        :param username: str - The user to mark as a mod
        """
        self.mods.add(username)

    def remove_mod(self, username):
        """
        Marks a user as not a mod in the channel.
        :param username: str - The user to mark as not a mod
        """
        self.mods.discard(username)

    def is_mod(self, username):
        """
        Checks if a user is a mod in the current channel.
        :param username: str - The user to check mod status for
        """
        return username in self.mods or username == self.owner

    def add_viewer(self, username):
        """
        Marks a user as a viewer of the current channel.
        :param username: str - The user to mark as a viewer
        """
        self.viewers.add(username)

    def remove_viewer(self, username):
        """
        Marks a user as not a viewer of the current channel.
        :param username: str - The user to mark as not a viewer
        """
        self.viewers.discard(username)
