from collections import OrderedDict
import json
import os
import sys


########################################################################################################################
#  Required settings; filled from file
########################################################################################################################
BROADCASTER_NAME = 'Your_Twitch_Name'
BOT_NAME = 'Twitch_Bot_Name'
BOT_OAUTH = 'oauth:bot_oauth_code'

########################################################################################################################
#  Optional settings; filled from file
########################################################################################################################

# Lets other people use a shared instance of your bot in their channel; disable if bot gets laggy
ENABLE_REQUEST_JOIN = True

########################################################################################################################
# Core settings; probably shouldn't change these
########################################################################################################################
# Twitch settings
IRC_SERVER = 'irc.twitch.tv'
IRC_PORT = 6667
IRC_POLL_TIMEOUT = 0.5
IRC_RECV_SIZE = 1024
# If Twitch sends a bunch of messages at once, it chunks it into multiple sends that may be delayed
IRC_CHUNK_DELAY = 0.15
# Rate-limit protection: 20 commands within 30 second period, or 1.5 second sleep time
# Whisper rate-limit is actually 3 per second, 100 per minute (0.6 seconds) but to be safe we share the same cooldown
IRC_SEND_COOLDOWN = 1.6
# Rate-limit protection: 50 JOINs per 15 seconds, or 0.3 sleep time
IRC_JOIN_SLEEP_TIME = 0.35

# Bot settings
RESTART_ON_CRASH = False
DATA_PATH = 'data'
SETTINGS_FILE_PATH = 'settings.txt'
CHANNEL_DATA_PATH = os.path.join(DATA_PATH, 'channels')
PLAYER_DATA_PATH = os.path.join(DATA_PATH, 'players')

# Game settings
EXP_LEVELS = [0, 3, 7, 12, 18, 25, 33, 42, 52, 63,
              75, 88, 102, 117, 133, 150, 168, 187, 207, 228,
              250, 273, 297, 322, 348, 375, 403, 432, 462, 493,
              0]
LEVEL_CAP = 30
PRESTIGE_COST = 30000
PRESTIGE_GOLD_AMP = 0.05
# How long there is for user interaction between quest advance sections
QUEST_DURATION = 12
QUEST_DEFAULT_COOLDOWN = 90

########################################################################################################################
# Dynamically loaded settings
########################################################################################################################
REQUIRED_STRING = 'REQUIRED'
OPTIONAL_STRING = 'OPTIONAL'
DEFAULT_SETTINGS_JSON = OrderedDict([
    (REQUIRED_STRING, OrderedDict([
        ('BROADCASTER_NAME', BROADCASTER_NAME),
        ('BOT_NAME', BOT_NAME),
        ('BOT_OAUTH', BOT_OAUTH)
    ])),
    (OPTIONAL_STRING, OrderedDict([
        ('ENABLE_REQUEST_JOIN', ENABLE_REQUEST_JOIN)
    ]))]
)


def load_settings_file():
    if os.path.isfile(SETTINGS_FILE_PATH):
        with open(SETTINGS_FILE_PATH) as json_data:
            settings_json = json.load(json_data)

        # Iterate over known variable names and change all the module's variables to the ones from file, if any
        module = sys.modules[__name__]
        for key, value in DEFAULT_SETTINGS_JSON[REQUIRED_STRING].items():
            setattr(module, key, settings_json[REQUIRED_STRING].get(key, value))
        for key, value in DEFAULT_SETTINGS_JSON[OPTIONAL_STRING].items():
            setattr(module, key, settings_json[OPTIONAL_STRING].get(key, value))
    else:
        settings_json = DEFAULT_SETTINGS_JSON
        # Write to file since it went missing
        with open(SETTINGS_FILE_PATH, 'w') as json_data:
            json.dump(settings_json, json_data, indent=4)
