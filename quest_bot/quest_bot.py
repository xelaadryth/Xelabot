from .quest_channel_manager import QuestChannelManager
from .quest_player_manager import QuestPlayerManager
from utils.commands import Commands
from twitch.twitch_bot import TwitchBot


class QuestBot(TwitchBot):
    """
    Bot with commands for quest mode.
    """
    def __init__(self, nickname, oauth):
        """
        :param nickname: str - The bot's username - must be lowercase
        :param oauth: str - The bot's oauth
        """
        super().__init__(nickname, oauth)

    def initialize(self):
        print('Initializing channel manager...')
        self.channel_manager = QuestChannelManager(self)

        print('Initializing player manager...')
        self.player_manager = QuestPlayerManager(self)

        # Commands for direct whispers to the bot
        self.whisper_commands = Commands(exact_match_commands={
            '!faq': self.faq_whisper,
            '!gold': self.stats_whisper,
            '!exp': self.stats_whisper,
            '!stats': self.stats_whisper,
            '!prestige': self.try_prestige
        })

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
