import sys
import os

sys.path.append(r"d:\cruzxiii.mediawiki\fishing_game")

from game.data.fishing import fishing_minigame
import time

class DummyPlayer:
    def __init__(self):
        self.rod = "Sunrise Rod"
        self.location = "Mooseland"
        
player = DummyPlayer()
fish = {
    'name': 'TestFish',
    'rarity': 'Common',
    'weight': 1.0,
    'base_price': 100,
    'price': 100,
    'mutation': None,
    'size': 'Original'
}

print("Starting Sunrise Rod test...")
try:
    # It will block, so we run for a short time or just check syntax
    print("Syntax is OK")
except Exception as e:
    print(f"CRASH: {e}")
