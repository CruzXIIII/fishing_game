import sys
import os
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import unittest

class TestGame(unittest.TestCase):
    def test_game(self):
        from game.data.player import Player
        from game.data.shop import shop_menu

        player = Player("test_save.json")
        player.money = 1000000

        # Volcano Shop
        inputs = ['4', '1', '', '0', '5']  # Added enter after buy
        def mock_input(prompt=""):
            if inputs:
                return inputs.pop(0)
            return '5'

        import builtins
        original_input = builtins.input
        builtins.input = mock_input

        try:
            player.location = "Mount. Betalee!"
            shop_menu(player)
        finally:
            builtins.input = original_input

        # Beach Vendors
        inputs = ['4', '1', '', '0', '5']
        def mock_input2(prompt=""):
            if inputs:
                return inputs.pop(0)
            return '5'

        builtins.input = mock_input2
        try:
            player.location = "Beach of Sovereign"
            shop_menu(player)
        finally:
            builtins.input = original_input

if __name__ == '__main__':
    unittest.main()
