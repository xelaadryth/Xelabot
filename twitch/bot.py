import socket
import time
import traceback

from .channel_manager import ChannelManager
from .commands import Commands
from .player_manager import PlayerManager
from utils.timer_thread import TimerThread

import settings


class Bot:
    """
    Sends and receives messages to and from IRC channels.
    """
    def __init__(self, nickname, oauth):
        """
        :param nickname: str - The bot's username - must be lowercase
        :param oauth: str - The bot's oauth
        """
        self.nickname = nickname
        self.oauth = oauth

        # Initializing commands from generic IRC messages
        self.irc_commands = Commands(starts_with_commands={
            'ping': lambda **kwargs: self.send_pong(kwargs['command'].split()[1]),
            ':tmi.twitch.tv notice * :error logging in': lambda **_: self.login_failure(),
            ':tmi.twitch.tv notice * :login unsuccessful': lambda **_: self.login_failure()
        })
        # Commands for direct whispers to the bot
        self.whisper_commands = Commands(exact_match_commands={
            '!faq': self.faq_whisper,
            '!gold': self.stats_whisper,
            '!exp': self.stats_whisper,
            '!stats': self.stats_whisper,
            '!prestige': self.try_prestige
        })

        # Initializing socket
        self.irc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc_sock.settimeout(settings.IRC_POLL_TIMEOUT)

        print('Initializing channel manager...')
        self.channel_manager = ChannelManager(self)
        print('Initializing player manager...')
        self.player_manager = PlayerManager(self)

    def __send_raw_instant(self, msg_str):
        """
        Sends a raw IRC message with no rate-limiting concerns.
        :param msg_str:
        :return:
        """
        print('> ' + msg_str)
        self.irc_sock.send(bytes(msg_str + '\r\n', 'UTF-8'))

    def send_raw(self, msg_str):
        """
        Sends a raw IRC message with post-delay to be consistent with rate-limiting.
        :param msg_str: str - The raw IRC message to be sent
        """
        self.__send_raw_instant(msg_str)

        # Prevent rate-limiting
        time.sleep(settings.IRC_SEND_COOLDOWN)

    def recv_raw(self):
        """
        Receives a raw IRC message.
        :return: str - The raw IRC message received
        """
        try:
            buf = self.irc_sock.recv(settings.IRC_RECV_SIZE)
            total_data = buf

            if not buf:
                    raise Exception('Socket connection broken.')

            # Keep trying to pull until there's nothing left.
            while len(buf) == settings.IRC_RECV_SIZE:
                buf = self.irc_sock.recv(settings.IRC_RECV_SIZE)
                total_data += buf
                # Sometimes there's a delay between different parts of the message
                time.sleep(settings.IRC_CHUNK_DELAY)
                if not buf:
                    raise Exception('Socket connection broken.')
            return str(total_data, encoding='UTF-8').strip('\r\n')
        except socket.timeout:
            # We quickly time out if there's no messages to receive as set by socket set timeout in the init
            return None

    def connect(self):
        """
        Connect to the IRC server and join the intended channels.
        """
        print('Connecting to Twitch IRC service...')
        self.irc_sock.connect((settings.IRC_SERVER, settings.IRC_PORT))
        self.__send_raw_instant('PASS ' + self.oauth)
        self.__send_raw_instant('USER {0} {0} {0} :{0}'.format(self.nickname))
        self.__send_raw_instant('NICK ' + self.nickname)

        # Bot should always join the broadcaster's channel
        if settings.BROADCASTER_NAME not in self.channel_manager.channels and (
                settings.BROADCASTER_NAME != 'your_lowercase_twitch_name'):
            print('Adding broadcaster to channel data...')
            self.channel_manager.add_channel(settings.BROADCASTER_NAME)

        for channel_name, channel in self.channel_manager.channels.items():
            if channel.channel_settings['auto_join']:
                print('Joining channel: {}...'.format(channel_name))
                # Join rate-limiting is at a rate of 50 joins per 15 seconds
                self.__send_raw_instant('JOIN #' + channel_name)
                time.sleep(settings.IRC_JOIN_SLEEP_TIME)

        # Enable twitch badges/tags
        self.__send_raw_instant('CAP REQ :twitch.tv/tags')
        # Enable whisper receiving
        self.__send_raw_instant('CAP REQ :twitch.tv/commands')

    def send_pong(self, server):
        """
        Send a keep-alive message when prompted with a ping.
        :param command: str - IRC server ping message of the form "PING :tmi.twitch.tv"
        """
        # Guaranteed to be at least two string tokens from the check in the main run loop
        self.__send_raw_instant('PONG ' + server)

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
        # It doesn't matter what channel we use to send whispers, but our own channel is safest
        self.send_msg(self.nickname, '/w {} {}'.format(target_name, msg_str))

    @staticmethod
    def login_failure():
        """
        If we fail to login, raise an exception.
        """
        raise RuntimeError('Failed to login, most likely invalid login credentials.')

    def faq_whisper(self, display_name=None, **_):
        if not display_name:
            return
        self.send_whisper(display_name.lower(),
                          'Information and an FAQ on Xelabot can be found at: http://github.com/Xelaadryth/Xelabot')

    def stats_whisper(self, display_name=None, **_):
        if not display_name:
            return
        self.player_manager.whisper_stats(display_name.lower())

    def try_prestige(self, display_name=None, **_):
        if not display_name:
            return
        self.player_manager.prestige(display_name.lower())

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

            display_name, is_mod, is_sub = Bot.parse_tags(raw_msg_tokens[0][1:])

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

        # Skip the message if it's from an invalid channel
        if channel_name not in self.channel_manager.channels.keys():
            print("Message from invalid channel: #" + channel_name)
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

        if whisper_target != self.nickname:
            print('Invalid whisper target: {}'.format(whisper_target))
            return

        self.whisper_commands.execute_command(msg, display_name=display_name)

    def handle_msg(self, raw_msg):
        """
        Given an arbitrary IRC message, handle it as necessary.
        :param raw_msg: str - The IRC raw message
        """
        if raw_msg:
            print(raw_msg)
        raw_msg_tokens = raw_msg.split()

        self.irc_commands.execute_command(raw_msg)

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

    def run(self):
        """
        Core update loop for the bot. Checks for completed timer callbacks and then handles input.
        """
        while True:
            # Check to see if any timers completed and activate their callbacks
            TimerThread.check_timers()

            raw_msgs = self.recv_raw()

            # We return None if we timed out on the receive in settings.IRC_POLL_TIMEOUT seconds to check our timers
            # or if we failed to receive messages
            if raw_msgs is None:
                continue

            # Splitting on \r\n allows reading of multiple commands with one recv
            for raw_msg in raw_msgs.split('\r\n'):
                self.handle_msg(raw_msg)

        raise RuntimeError('Exited execution loop.')
