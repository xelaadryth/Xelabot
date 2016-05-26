import time
import traceback

from utils.cmd import pause
from quest_bot.quest_bot import QuestBot
import settings
from utils.auto_update import clear_temp_files, try_update


def run_bot():
    """
    Simply starts the bot, and restarts on crash.
    """
    try:
        # Create the bot
        bot = QuestBot(settings.BOT_NAME, settings.BROADCASTER_NAME, settings.BOT_OAUTH)
        bot.connect()
        bot.run()
    except Exception as e:
        print('BOT CRASHED: ' + repr(e))
        traceback.print_exc()

        # If the bot crashes for whatever reason, restart it
        if settings.AUTO_RESTART_ON_CRASH:
            time.sleep(5)
            run_bot()

        pause()

if __name__ == '__main__':
    clear_temp_files()
    try:
        try_update()
    except Exception as e:
        print('Update failed: ' + repr(e))
        traceback.print_exc()
        clear_temp_files()
        print('Continuing execution as normal!')
    settings.load_settings_file()
    run_bot()
