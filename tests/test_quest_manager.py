import unittest
from unittest.mock import MagicMock

from quest.quest_manager import QuestManager
from quest.quest_state import QuestState
from quest.quests import QUEST_LIST


class TestQuestManager(unittest.TestCase):
    def setUp(self):
        self.channel = MagicMock()

        self.player1 = 'Player1'
        self.player2 = 'Player2'
        self.player3 = 'Player3'
        self.player4 = 'Player4'

        self.quest_manager = QuestManager(self.channel)

    def test_disabled(self):
        self.quest_manager.disable_questing()
        self.quest_manager.commands.execute_command(self.player1, '!quest')
        self.assertEqual(self.channel.send_msg.call_count, 1)
        self.assertIsNone(self.quest_manager.quest_timer)
        self.assertIs(self.quest_manager.quest_state, QuestState.disabled)

    def test_quest_disable_enable(self):
        self.quest_manager.enable_questing()
        self.assertIs(self.quest_manager.quest_state, QuestState.ready)
        self.quest_manager.commands.execute_command(self.player1, '!quest')
        # Only the first player "starts" the quest, second player shouldn't increase the reply count
        self.quest_manager.commands.execute_command(self.player2, '!quest')
        self.quest_manager.commands.execute_command(self.player1, '!quest')
        self.assertIs(self.quest_manager.quest_state, QuestState.forming_party)
        self.assertEqual(self.channel.send_msg.call_count, 1)
        self.assertIsNotNone(self.quest_manager.quest_timer)

        self.quest_manager.disable_questing()
        self.assertIs(self.quest_manager.quest_state, QuestState.disabled)
        # Every request should say that we're disabled
        self.quest_manager.commands.execute_command(self.player2, '!quest')
        self.quest_manager.commands.execute_command(self.player1, '!quest')
        self.quest_manager.commands.execute_command(self.player1, '!quest')
        self.assertIs(self.quest_manager.quest_state, QuestState.disabled)
        self.assertEqual(self.channel.send_msg.call_count, 4)
        self.assertIsNone(self.quest_manager.quest_timer)

        self.quest_manager.enable_questing()
        self.assertIs(self.quest_manager.quest_state, QuestState.ready)
        self.quest_manager.commands.execute_command(self.player1, '!quest')
        self.assertIs(self.quest_manager.quest_state, QuestState.forming_party)
        self.assertEqual(self.channel.send_msg.call_count, 5)
        self.assertIsNotNone(self.quest_manager.quest_timer)

    def test_party_form(self):
        self.quest_manager.enable_questing()
        self.assertIs(self.quest_manager.quest_state, QuestState.ready)
        self.quest_manager.commands.execute_command(self.player1, '!quest')
        self.quest_manager.commands.execute_command(self.player1, '!quest')
        self.quest_manager.commands.execute_command(self.player2, '!quest')
        self.quest_manager.commands.execute_command(self.player1, '!quest')
        self.quest_manager.commands.execute_command(self.player3, '!quest')
        self.quest_manager.commands.execute_command(self.player3, '!quest')
        self.quest_manager.commands.execute_command(self.player2, '!quest')

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        self.quest_manager.quest_advance()

        self.assertIs(self.quest_manager.quest_state, QuestState.active)
        self.assertIsNotNone(self.quest_manager.quest_timer)
        quest = self.quest_manager.quest
        self.assertIsNotNone(quest)
        # Party should be ordered the same
        self.assertSequenceEqual(quest.party, [self.player1, self.player2, self.player3])
        self.assertIn(type(quest), QUEST_LIST[3])


if __name__ == '__main__':
    unittest.main()
