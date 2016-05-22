import settings
import traceback

from utils.bot import Bot


def run_bot():
    """
    Simply starts the bot, and restarts on crash.
    """
    try:
        # Create the bot
        bot = Bot(settings.BOT_NAME, settings.BOT_OAUTH)
        bot.connect()
        bot.run()
    except Exception as e:
        print("BOT CRASHED: " + str(e))
        traceback.print_exc()

        # If the bot crashes for whatever reason, restart it
        if settings.RESTART_ON_CRASH:
            run_bot()

if __name__ == "__main__":
    run_bot()
