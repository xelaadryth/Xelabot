from .quest_channel_manager import QuestChannelManager
from .quest_player_manager import QuestPlayerManager
from utils.command_set import CommandSet
from twitch.twitch_bot import TwitchBot


class QuestBot(TwitchBot):
    """
    Bot with commands for quest mode.
    """
    def __init__(self, bot_name, owner_name, oauth):
        """
        :param bot_name: str - The bot's username
        :param owner_name: str - The owner's username
        :param oauth: str - The bot's oauth
        """
        super().__init__(bot_name, owner_name, oauth)

    def initialize(self):
        print('Initializing channel manager...')
        self.channel_manager = QuestChannelManager(self)

        print('Initializing player manager...')
        self.player_manager = QuestPlayerManager(self)

        # Commands for direct whispers to the bot
        self.whisper_commands = CommandSet(exact_match_commands={
            '!faq': self.faq_whisper,
            '!gold': self.stats_whisper,
            '!exp': self.stats_whisper,
            '!stats': self.stats_whisper,
            '!prestige': self.try_prestige
        })

    def faq_whisper(self, display_name):
        if not display_name:
            return
        self.send_whisper(display_name,
                          'Information and an FAQ on Xelabot can be found at: http://github.com/Xelaadryth/Xelabot')

    def stats_whisper(self, display_name):
        if not display_name:
            return
        self.player_manager.whisper_stats(display_name)

    def try_prestige(self, display_name):
        if not display_name:
            return
        self.player_manager.prestige(display_name)
