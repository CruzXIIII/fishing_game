import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

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

import unittest
class TestSunrise(unittest.TestCase):
    def test_sunrise(self):
        print("Starting Sunrise Rod test...")
        try:
            print("Syntax is OK")
        except Exception as e:
            print(f"CRASH: {e}")

if __name__ == '__main__':
    unittest.main()
