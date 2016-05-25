import time
import traceback

from .channel_manager import ChannelManager
from.player_manager import PlayerManager
from utils.command_set import CommandSet
from utils.irc_bot import IRCBot
import settings


class TwitchBot(IRCBot):
    """
    Sends and receives messages to and from Twitch channels.
    """
    def __init__(self, nickname, oauth):
        """
        :param nickname: str - The bot's username
        :param oauth: str - The bot's oauth
        """
        super().__init__(nickname, oauth)

        self.channel_manager = None
        self.player_manager = None
        self.whisper_commands = None

        self.initialize()

    def initialize(self):
        print('Initializing channel manager...')
        self.channel_manager = ChannelManager(self)

        print('Initializing player manager...')
        self.player_manager = PlayerManager(self)

        # Commands for direct whispers to the bot
        self.whisper_commands = CommandSet()

    def connect(self):
        """
        Connect to the IRC server and join the intended channels.
        """
        super().connect()

        # Enable twitch badges/tags
        self.send_raw_instant('CAP REQ :twitch.tv/tags')
        # Enable whisper receiving
        self.send_raw_instant('CAP REQ :twitch.tv/commands')

        # Bot should always join its own channel and the broadcaster's channel
        self.channel_manager.join_channel(settings.BOT_NAME)
        self.channel_manager.join_channel(settings.BROADCASTER_NAME)

        for channel_name, channel in self.channel_manager.channels.items():
            if channel_name not in [settings.BROADCASTER_NAME.lower(), settings.BOT_NAME.lower()] and (
                    channel.channel_settings['auto_join']):
                print('Joining channel: {}...'.format(channel_name))
                # Join rate-limiting is at a rate of 50 joins per 15 seconds
                self.send_raw_instant('JOIN #' + channel_name)
                time.sleep(settings.IRC_JOIN_SLEEP_TIME)

    def send_msg(self, channel_name, msg_str):
        """
        Send a message to an IRC chatroom.
        :param channel_name: str - The channel to post a message to
        :param msg_str: str - The message to post
        """
        self.send_raw('PRIVMSG #{} :{}'.format(channel_name, msg_str))

    def send_whisper(self, target_name, msg_str):
        """
        Send a whisper to a user.
        :param target_name: str - The user to whisper
        :param msg_str: str - The message to whisper
        """
        target_name = target_name.lower()
        # It doesn't matter what channel we use to send whispers, but our own channel is safest
        self.send_msg(self.nickname, '/w {} {}'.format(target_name, msg_str))

    @staticmethod
    def parse_tags(raw_tags):
        """
        Given raw tags, parse them and return some crucial user info. Looks something like this:

            badges=broadcaster/1,turbo/1;color=#573894;display-name=BroadcastingDude;emotes=;mod=0;room-id=12345678;
                subscriber=0;turbo=1;user-id=12345678;user-type=

            badges=moderator/1;color=#00FF7F;display-name=CoolMod;emotes=;mod=1;room-id=12345678;subscriber=0;
                turbo=0;user-id=87654321;user-type=mod

            badges=;color=#8A2BE2;display-name=Pleb;emotes=;mod=0;room-id=12345678;subscriber=0;turbo=0;
                user-id=11111111;user-type=

        :param raw_tags: str - The first token of the IRC message, without the @ symbol
        :return: tuple<str, bool, bool> - A tuple of user info: (display_name, is_mod, is_sub)
        """
        display_name = None
        is_mod = False
        is_sub = False
        for raw_tag in raw_tags.split(';'):
            raw_tag_split = raw_tag.split('=')

            key = raw_tag_split[0]
            value = raw_tag_split[1]

            if key == 'display-name':
                display_name = value
            elif key == 'mod' and value == '1':
                is_mod = True
            elif key == 'subscriber' and value == '1':
                is_sub = True

        return display_name, is_mod, is_sub

    @staticmethod
    def parse_msg(raw_msg):
        """
        Given a raw IRC message that is either a whisper or a channel message, parse out useful information.
        :param raw_msg: str - The IRC raw message that includes the type PRIVMSG or WHISPER
        :return: tuple<str, str, str, bool, bool> - A tuple of user info:
                 (Display_Name, channel/whisper target, message, is_mod, is_sub)
        """
        try:
            raw_msg_tokens = raw_msg.split(maxsplit=4)

            display_name, is_mod, is_sub = TwitchBot.parse_tags(raw_msg_tokens[0][1:])

            # If we fail to get the display name for whatever reason, get it from the raw IRC message
            if display_name is None:
                display_name = raw_msg_tokens[1].split('!')[0][1:]
            target_name = raw_msg_tokens[3]
            # Channel messages have channel name starting with '#', whispers have no symbol
            if target_name.startswith('#'):
                target_name = target_name[1:]
            msg = raw_msg_tokens[4][1:]

            return display_name, target_name, msg, is_mod, is_sub
        except Exception as e:
            print('Unable to parse message "{}": {}'.format(raw_msg, repr(e)))
            return None

    def handle_channel_msg(self, raw_msg):
        """
        Given a raw IRC message identified as a channel message, handle it as necessary. Looks something like this:

            @TAGS, :USER!USER@USER.tmi.twitch.tv, PRIVMSG, #CHANNEL :MSG

            @badges=;color=#8A2BE2;display-name=Pleb;emotes=;mod=0;room-id=12345678;subscriber=0;turbo=0;
                user-id=11111111;user-type= :pleb!pleb@pleb.tmi.twitch.tv PRIVMSG #sometwitchuser :Normal user.

        :param raw_msg: str - The IRC raw message that includes the type PRIVMSG
        """
        display_name, channel_name, msg, is_mod, is_sub = self.parse_msg(raw_msg)

        # All channel commands start with '!'
        if msg[0] != '!':
            return

        # Skip the message if it's from an invalid channel; Xelabot should only be listening to channels it's in.
        if channel_name not in self.channel_manager.channels.keys():
            print("Message from channel not added to Channel Manager: #" + channel_name)
            return

        channel = self.channel_manager.channels[channel_name]

        # Channel specific commands, like quest commands
        channel.check_commands(display_name, msg, is_mod, is_sub)

        if msg in self.whisper_commands.exact_match_commands:
            self.send_whisper(display_name.lower(), 'Try whispering that command to Xelabot instead!')

    def handle_whisper(self, raw_msg):
        """
        Given a raw IRC message identified as a whisper, handle it as necessary. Looks something like this:

            @TAGS :USER!USER@USER.tmi.twitch.tv WHISPER BOT_NAME :MSG

            @badges=;color=#8A2BE2;display-name=Pleb;emotes=;message-id=2;thread-id=12348765_56784321;turbo=0;
                user-id=11111111;user-type= :pleb!pleb@pleb.tmi.twitch.tv WHISPER xelabot :This is a whisper.

        :param raw_msg: str - The IRC raw message that includes the type WHISPER
        """
        display_name, whisper_target, msg, is_mod, is_sub = self.parse_msg(raw_msg)

        if whisper_target != self.nickname.lower():
            print('Invalid whisper target: {}'.format(whisper_target))
            return

        self.whisper_commands.execute_command(display_name, msg)

    def handle_msg(self, raw_msg):
        """
        Given an arbitrary IRC message, handle it as necessary.
        :param raw_msg: str - The IRC raw message
        """
        super().handle_msg(raw_msg)

        raw_msg_tokens = raw_msg.split()

        if len(raw_msg_tokens) < 3:
            return
        try:
            if raw_msg_tokens[2] == 'PRIVMSG':
                self.handle_channel_msg(raw_msg)
            elif raw_msg_tokens[2] == 'WHISPER':
                self.handle_whisper(raw_msg)
        except Exception as e:
            print('IRC message handler error: {}'.format(repr(e)))
            traceback.print_exc()
