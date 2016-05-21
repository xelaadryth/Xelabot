import settings
import socket
import time

from utils.channel_manager import ChannelManager
from utils.player_manager import PlayerManager


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

        self.irc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc_sock.settimeout(settings.IRC_POLL_TIMEOUT)

        self.last_sent_message = None

        self.channel_manager = ChannelManager(self)
        self.player_manager = PlayerManager(self)

        # All the TimerThreads
        self.timer_callbacks = set()

    def send_raw(self, msg_str):
        """
        Sends a raw IRC message.
        :param msg_str: str - The raw IRC message to be sent
        """
        self.irc_sock.send(bytes(msg_str + "\r\n", "UTF-8"))
        self.last_sent_message = msg_str

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
                    raise Exception("Socket connection broken.")

            # Keep trying to pull until there's nothing left.
            while len(buf) == settings.IRC_RECV_SIZE:
                buf = self.irc_sock.recv(settings.IRC_RECV_SIZE)
                total_data += buf
                # Sometimes there's a delay between different parts of the message
                time.sleep(settings.IRC_CHUNK_DELAY)
                if not buf:
                    raise Exception("Socket connection broken.")
            return str(total_data, encoding="UTF-8").strip("\r\n")
        except socket.timeout:
            # We quickly time out if there's no messages to receive as set by socket set timeout in the init
            return None

    def connect(self):
        """
        Connect to the IRC server and join the intended channels.
        """
        self.irc_sock.connect((settings.IRC_SERVER, settings.IRC_PORT))
        self.send_raw("PASS " + self.oauth)
        self.send_raw("USER " + self.nickname + " " + self.nickname + " " + self.nickname + " :" + self.nickname)
        self.send_raw("NICK " + self.nickname)

        # Bot should always join the broadcaster's channel
        if settings.BROADCASTER_NAME not in self.channel_manager.channels:
            self.channel_manager.add_channel(settings.BROADCASTER_NAME)

        for channel_name, channel in self.channel_manager.channels.items():
            if channel.channel_settings['auto_join']:
                # Normally we'd need to sleep for 0.3 seconds here to prevent JOIN rate-limiting,
                # but our send delay is already longer than that
                self.send_raw("JOIN #" + channel_name)

    def send_pong(self, server_str):
        """
        Send a keep-alive message when prompted with a ping.
        :param server_str: Server to respond to.
        """
        self.send_raw("PONG " + server_str)

    def send_msg(self, channel_name, msg_str):
        """
        Send a message to an IRC chatroom.
        :param channel_name: str - The channel to post a message to
        :param msg_str: str - The message to post
        """
        print("[#{}] {}: {}".format(channel_name, self.nickname, msg_str))
        self.send_raw("PRIVMSG #" + channel_name + " :" + msg_str)

    def send_whisper(self, target_name, msg_str):
        """
        Send a whisper to a user
        :param target_name: str - The user to whisper
        :param msg_str: str - The message to whisper
        """
        self.send_msg(target_name, '/w {} {}'.format(target_name, msg_str))

    def run(self):
        """
        Core update loop for the bot. Checks for completed timer callbacks and then handles input.
        """
        while True:
            # Check to see if any timers completed and activate their callbacks
            self.timer_callbacks = {timer for timer in self.timer_callbacks if not timer.is_complete()}

            # =================================================================================
            irc_msgs = self.recv_raw()

            # We return None if we timed out on the receive in settings.IRC_POLL_TIMEOUT seconds to check our timers
            # or if we failed to receive messages
            if irc_msgs is None:
                continue

            # Splitting on \r\n allows reading of multiple commands with one recv
            for irc_msg in irc_msgs.split("\r\n"):
                if irc_msg:
                    print(irc_msg)
                irc_msg_split = irc_msg.split()

                if len(irc_msg_split) < 2:
                    continue

                if irc_msg_split[1] == "PRIVMSG":
                    # Signifies a chat message from a channel
                    if irc_msg_split[2][0] == "#":
                        user = irc_msg_split[0].split('!')[0][1:].lower()
                        twitch_msg = "PRIVMSG #".join(irc_msg.split("PRIVMSG #")[1:])
                        channel_name = twitch_msg.split(" :")[0].lower()
                        original_msg = " :".join(twitch_msg.split(" :")[1:])
                        msg = original_msg.lower()

                        #print("(" + channel_name + ") " + user + ": " + msg)

                        # Skip the message if it's from an invalid channel
                        if channel_name not in self.channel_manager.channels.keys():
                            print("Message from invalid channel: #" + channel_name)
                            continue

                        channel = self.channel_manager.channels[channel_name]

                        # Channel join command only works in the bot's channel
                        if channel_name == "xelaadryth":
                            if msg == "!requestjoin":
                                self.channel_manager.add_channel(user)
                                self.send_raw("JOIN #" + user)
                                channel.send_msg("Xelabot has now joined " + user + "'s channel.")

                        # Channel specific commands, like quest commands
                        channel.check_commands(user, original_msg)

                        # Common commands
                        if msg == "!xelabot":
                            channel.send_msg("Information and an FAQ on Xelabot can be found at " +
                                             "https://dl.dropboxusercontent.com/u/90882877/Xelabot/Xelabot.txt")
                        elif msg == "!requestleave":
                            self.channel_manager.delete_channel(user)
                            self.send_raw("PART #" + user)
                            channel.send_msg("Xelabot has left " + user + "'s channel.")
                        elif msg == "!gold" or msg == "!exp":
                            channel.send_msg("Please use !stats instead, this command has been deprecated.")
                        elif msg == "!stats":
                            channel.send_msg("You can view the stats page at " +
                                             "https://dl.dropboxusercontent.com/u/90882877/Xelabot/PlayerInfo.txt")
                        elif msg == "!prestige":
                            if self.player_manager.prestige(user):
                                channel.send_msg(user + " has prestiged, and is now prestige level " +
                                                 str(self.player_manager.players[user]["prestige"]) + "!")
                            else:
                                channel.send_msg(user + " does not have enough exp/gold to prestige, requires " +
                                                 str(settings.LEVELS[settings.LEVEL_CAP-1]) + " exp and " +
                                                 str(settings.PRESTIGE_COST) + " gold.")
                        elif msg.startswith("action commits sudoku"):
                            channel.send_msg("/me un-sudokus " + user + ".")
                        elif msg.startswith("action sudokus"):
                            channel.send_msg("/me un-sudokus " + user + ".")

                        # Mod commands
                        if user == channel_name or channel.is_mod(user) or user == "xelaadryth":
                            if msg == "!questoff":
                                self.channel_manager.disable_quest(channel_name)
                            elif msg == "!queston":
                                self.channel_manager.enable_quest(channel_name)
                            elif msg.startswith("!questcooldown "):
                                try:
                                    cooldown = int(msg.split()[1])
                                    if cooldown >= 5:
                                        self.channel_manager.set_quest_cooldown(channel_name, cooldown)
                                        channel.send_msg("Channel cooldown set to " + msg.split()[1] + " seconds.")
                                    else:
                                        channel.send_msg("Cooldown must be at least 5 seconds.")
                                except:
                                    channel.send_msg("Invalid syntax for !questcooldown.")

                        # Personal commands
                        if user == settings.BROADCASTER_NAME:
                            if msg.startswith("!addgold "):
                                gold_request = msg.split()

                                try:
                                    gold_amount = int(gold_request[1])
                                    target_user = gold_request[2].lower()

                                    self.player_manager.add_gold(target_user, gold_amount, False)

                                    channel.send_msg("Added " + str(gold_amount) + " gold to " + target_user +
                                                     "'s stockpile for a total of " +
                                                     str(self.player_manager.players[target_user]['gold']) + " gold!")
                                except:
                                    channel.send_msg("Invalid syntax for !addgold.")
                            elif msg.startswith("!addexp "):
                                exp_request = msg.split()

                                try:
                                    exp_amount = int(exp_request[1])
                                    target_user = exp_request[2]

                                    self.player_manager.add_exp(target_user, exp_amount)
                                    exp = self.player_manager.get_exp(target_user)
                                    channel.send_msg("Added " + str(exp_amount) + " exp to " + target_user +
                                                     ". " + target_user + " now has " + str(exp) +
                                                     " exp and is level " + str(Settings.get_level(exp)) + "!")
                                except:
                                    self.send_msg(channel_name, "Invalid syntax for !addexp.")
                            elif msg.startswith("!try "):
                                try:
                                    channel.send_msg(msg[5:])
                                except:
                                    channel.send_msg("Invalid syntax for !try.")
                            elif msg.startswith("!say "):
                                try:
                                    split_msg = msg.split()
                                    target_channel = split_msg[1]
                                    self.channel_manager.channels[target_channel].send_msg(' '.join(split_msg[2:]))
                                except:
                                    channel.send_msg("Invalid syntax for !channeltry.")
                elif irc_msg_split[1] == "MODE":
                    if irc_msg_split[2][0] == "#":
                        channel_name = irc_msg_split[2][1:]
                        channel = self.channel_manager.channels[channel_name]
                        user = irc_msg_split[4]
                        if irc_msg_split[3] == "+o":
                            channel.add_mod(user)
                        elif irc_msg_split[3] == "-o":
                            channel.remove_mod(user)
                elif irc_msg_split[1] == "JOIN":
                    if irc_msg_split[2][0] == "#":
                        user = irc_msg_split[0].split('!')[0][1:].lower()
                        channel_name = irc_msg_split[2][1:].lower()

                        # Skip the message if it's from an invalid channel
                        if channel_name not in self.channel_manager.channels.keys():
                            print("Message from invalid channel: #" + channel_name)
                            continue

                        channel = self.channel_manager.channels[channel_name]

                        channel.add_viewer(user)
                elif irc_msg_split[1] == "PART":
                    if irc_msg_split[2][0] == "#":
                        user = irc_msg_split[0].split('!')[0][1:].lower()
                        channel_name = irc_msg_split[2][1:].lower()

                        # Skip the message if it's from an invalid channel
                        if channel_name not in self.channel_manager.channels.keys():
                            print("Message from invalid channel: #" + channel_name)
                            continue

                        channel = self.channel_manager.channels[channel_name]

                        channel.remove_viewer(user)
                elif irc_msg.startswith("PING"):
                    self.send_pong(irc_msg.split()[1])
                elif irc_msg.startswith(":tmi.twitch.tv NOTICE * :Error logging in"):
                    print("Login unsuccessful")
                elif irc_msg.startswith(":tmi.twitch.tv NOTICE * :Login unsuccessful"):
                    print("Login unsuccessful")

        print("Exited execution loop.")
