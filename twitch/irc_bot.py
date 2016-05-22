import socket
import time

from .commands import Commands
from utils.timer_thread import TimerThread

import settings


class IRCBot:
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

        # Initializing socket
        self.irc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc_sock.settimeout(settings.IRC_POLL_TIMEOUT)

    def send_raw_instant(self, msg_str):
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
        self.send_raw_instant(msg_str)

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
        print('Connecting to IRC service...')
        self.irc_sock.connect((settings.IRC_SERVER, settings.IRC_PORT))
        self.send_raw_instant('PASS ' + self.oauth)
        self.send_raw_instant('USER {0} {0} {0} :{0}'.format(self.nickname))
        self.send_raw_instant('NICK ' + self.nickname)

    def send_pong(self, server):
        """
        Send a keep-alive message when prompted with a ping.
        :param server: str - IRC server that sent a PING
        """
        # Guaranteed to be at least two string tokens from the check in the main run loop
        self.send_raw_instant('PONG ' + server)

    @staticmethod
    def login_failure():
        """
        If we fail to login, raise an exception.
        """
        raise RuntimeError('Failed to login, most likely invalid login credentials.')

    def handle_msg(self, raw_msg):
        """
        Given an arbitrary IRC message, handle it as necessary.
        :param raw_msg: str - The IRC raw message
        """
        if raw_msg:
            print(raw_msg)

        self.irc_commands.execute_command(raw_msg)

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
