from collections import OrderedDict
import json
import os
import sys


VERSION = '2.0.1.10'


########################################################################################################################
#  Required settings; filled from file
########################################################################################################################
BROADCASTER_NAME = 'Your_Twitch_Name'
BOT_NAME = 'Twitch_Bot_Name'
BOT_OAUTH = 'oauth:bot_oauth_code'

########################################################################################################################
#  Optional settings; filled from file
########################################################################################################################
# Auto-update the executable without prompting
AUTO_UPDATE_EXECUTABLE = False
# Log everything to file
LOG_TO_FILE = False
# Bot setting to restart if it crashes
AUTO_RESTART_ON_CRASH = False
# Lets other people use a shared instance of your bot in their channel; disable if bot gets laggy
ENABLE_REQUEST_JOIN = True

########################################################################################################################
# URL and file names for hosting associated bot files
########################################################################################################################
BASE_URL = 'https://dl.dropboxusercontent.com/u/90882877/Xelabot/'
VERSION_FILENAME = 'version.txt'
EXECUTABLE_FILENAME = 'xelabot.exe'
HELP_FILENAME = 'faq.txt'

########################################################################################################################
# External site dependencies
########################################################################################################################
# Format with lowercase streamer name and query for a json response
CHATTERS_URL = 'https://tmi.twitch.tv/group/user/{}/chatters'

########################################################################################################################
# Twitch and IRC settings
########################################################################################################################
# Twitch settings
IRC_SERVER = 'irc.twitch.tv'
IRC_PORT = 6667
IRC_POLL_TIMEOUT = 0.5
IRC_RECV_SIZE = 1024
# If Twitch sends a bunch of messages at once, it chunks it into multiple sends that may be delayed
IRC_CHUNK_DELAY = 0.15
# Whisper rate-limit is actually 3 per second, 100 per minute (0.6 seconds) but we share the same cooldown
# TODO: Faster mod cooldowns
# Rate-limit protection: 20 commands within 30 second period, or 1.5 second sleep time for non-mods
IRC_SEND_COOLDOWN = 1.6
# Rate-limit protection: 50 JOINs per 15 seconds, or 0.3 sleep time
IRC_JOIN_SLEEP_TIME = 0.35

########################################################################################################################
# Local file paths
########################################################################################################################
SETTINGS_FILENAME = 'settings.txt'
LOG_FILENAME = 'log.txt'
ERROR_FILENAME = 'error.txt'
DATA_FOLDER = 'data'
PLAYER_DATA_PATH = os.path.join(DATA_FOLDER, 'players')
CHANNEL_DATA_PATH = os.path.join(DATA_FOLDER, 'channels')

########################################################################################################################
# Temp files
########################################################################################################################
TEMP = 'temp_'
RENAME_SCRIPT_FILENAME = TEMP + 'rename.bat'
NEW_EXECUTABLE_FILENAME = TEMP + EXECUTABLE_FILENAME
FILES_TO_CLEAR_ON_LOAD = [RENAME_SCRIPT_FILENAME, NEW_EXECUTABLE_FILENAME, LOG_FILENAME, ERROR_FILENAME]

########################################################################################################################
# Quest settings
########################################################################################################################
EXP_LEVELS = [-1,
              0,   3,   7,   12,  18,  25,  33,  42,  52,  63,
              75,  88,  102, 117, 133, 150, 168, 187, 207, 228,
              250, 273, 297, 322, 348, 375, 403, 432, 462, 493]
LEVEL_CAP = len(EXP_LEVELS) - 1
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
        ('ENABLE_REQUEST_JOIN', ENABLE_REQUEST_JOIN),
        ('AUTO_UPDATE_EXECUTABLE', AUTO_UPDATE_EXECUTABLE),
        ('AUTO_RESTART_ON_CRASH', AUTO_RESTART_ON_CRASH),
        ('LOG_TO_FILE', LOG_TO_FILE)
    ]))]
)


def load_settings_file():
    if os.path.isfile(SETTINGS_FILENAME):
        with open(SETTINGS_FILENAME) as read_file:
            temp_settings_json = json.load(read_file, object_pairs_hook=OrderedDict)

        # Iterate over known variable names and change all the module's variables to the ones from file, if any
        module = sys.modules[__name__]
        settings_json = OrderedDict([
            (REQUIRED_STRING, OrderedDict()),
            (OPTIONAL_STRING, OrderedDict())
        ])
        for key, value in DEFAULT_SETTINGS_JSON[REQUIRED_STRING].items():
            newest_value = temp_settings_json[REQUIRED_STRING].get(key, value)
            setattr(module, key, newest_value)
            settings_json[REQUIRED_STRING][key] = newest_value
        for key, value in DEFAULT_SETTINGS_JSON[OPTIONAL_STRING].items():
            newest_value = temp_settings_json[OPTIONAL_STRING].get(key, value)
            setattr(module, key, temp_settings_json[OPTIONAL_STRING].get(key, value))
            settings_json[OPTIONAL_STRING][key] = newest_value
    else:
        settings_json = DEFAULT_SETTINGS_JSON

    # Write to file to make sure we have the latest data
    with open(SETTINGS_FILENAME, 'w') as write_file:
        json.dump(settings_json, write_file, indent=4)
