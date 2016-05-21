import os

########################################################################################################################
#  Required settings; add these immediately!
########################################################################################################################
BROADCASTER_NAME = "your_lowercase_twitch_name"
BOT_NAME = "bot_lowercase_twitch_name"
BOT_OAUTH = "oauth:bot_oauth_code"

########################################################################################################################
# Optional settings; change these as you want
########################################################################################################################
QUEST_DEFAULT_COOLDOWN = 90

########################################################################################################################
# Core settings; probably shouldn't change these
########################################################################################################################
# Twitch settings
IRC_SERVER = "irc.twitch.tv"
IRC_PORT = 6667
IRC_POLL_TIMEOUT = 0.5
IRC_RECV_SIZE = 1024
# If Twitch sends a bunch of messages at once, it chunks it into multiple sends that may be delayed
IRC_CHUNK_DELAY = 0.15
# Rate-limit protection: 20 commands within 30 second period, or 1.5 second sleep time
IRC_SEND_COOLDOWN = 1.6
# Rate-limit protection: 50 JOINs per 15 seconds, or 0.3 sleep time
IRC_JOIN_SLEEP_TIME = 0.35

# Bot settings
RESTART_ON_CRASH = True
DATA_PATH = 'data'
CHANNEL_DATA_PATH = os.path.join(DATA_PATH, 'channels')
PLAYER_DATA_PATH = os.path.join(DATA_PATH, 'players')

# Game settings
EXP_LEVELS = [0, 3, 7, 12, 18, 25, 33, 42, 52, 63,
              75, 88, 102, 117, 133, 150, 168, 187, 207, 228,
              250, 273, 297, 322, 348, 375, 403, 432, 462, 493]
LEVEL_CAP = 30
PRESTIGE_COST = 30000
PRESTIGE_GOLD_AMP = 0.05
# How long there is for user interaction between quest advance sections
QUEST_DURATION = 15
