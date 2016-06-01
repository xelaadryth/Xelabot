import os
import time

from quest_bot.quest_bot import QuestBot
import settings
from utils.auto_update import try_update
from utils.cmd import pause
from utils.logger import log, log_error


def run_bot():
    """
    Simply starts the bot, and restarts on crash.
    """
    try:
        # Create the bot
        bot = QuestBot(settings.BOT_NAME, settings.BROADCASTER_NAME, settings.BOT_OAUTH)
        bot.connect()
        bot.run()
    except Exception as e2:
        log_error('Bot crashed', e2)

        # If the bot crashes for whatever reason, restart it
        if settings.AUTO_RESTART_ON_CRASH:
            time.sleep(5)
            run_bot()

        pause()


def clear_temp_files():
    """
    Delete all files that don't need to persist across runs.
    """
    for filename in settings.FILES_TO_CLEAR_ON_LOAD:
        if os.path.isfile(filename):
            os.remove(filename)


if __name__ == '__main__':
    clear_temp_files()
    try:
        try_update()
    except Exception as e:
        log_error('Update failed', e)
        log('Continuing execution as normal!')
    settings.load_settings_file()
    run_bot()
