import sys
import os
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass
sys.path.append(os.path.join(os.path.dirname(__file__), 'game'))
from game.data.player import Player
from game.data.shop import shop_menu

def test():
    player = Player("test_save.json")
    player.money = 1000000  # Give some money to buy stuff
    
    # 1. Travel to Mount. Betalee
    print("Testing Travel to Mount. Betalee!")
    # Current location is Mooseland
    # Option 2 should be Mount. Betalee if Bematee is 1, let's see destinations
    # Destinations: Bematee, Mount. Betalee!, Beach of Sovereign
    # So Mount. Betalee is option 2
    
    player.location = "Mount. Betalee!"
    
    # 2. Volcano Shop
    print("Testing Volcano Shop")
    # In shop_menu, choice 4 is Volcano Vendor, then choice 1 is Buy Magma Rod, 0 is Back, 5 is leave
    inputs = ['4', '1', '0', '5']
    def mock_input(prompt=""):
        if inputs:
            val = inputs.pop(0)
            print(f"INPUT: {val}")
            return val
        return '5'
    
    import builtins
    builtins.input = mock_input
    
    try:
        shop_menu(player)
        print("Shop menu OK")
    except Exception as e:
        print(f"Exception in shop_menu: {e}")
        
    print(f"Player rod after shop: {player.rod}")

    # 3. Fish at Volcano
    print("Testing Fishing at Volcano")
    try:
        go_fishing(player)
        print("Fishing at Volcano OK")
    except Exception as e:
        print(f"Exception in go_fishing: {e}")

    # 4. Travel to Beach of Sovereign
    player.location = "Beach of Sovereign"
    print("Testing Beach Vendors")
    # In shop_menu, choice 4 is Beach Vendors, choice 1 is buy Celestial, 0 is Back, 5 is leave
    inputs = ['4', '1', '0', '5']
    try:
        shop_menu(player)
        print("Beach vendor OK")
    except Exception as e:
        print(f"Exception in Beach Vendors: {e}")

test()
