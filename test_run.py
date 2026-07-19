import sys
sys.path.append("fishing_game")
from game.ui.launcher import run_terminal, loading_screen
try:
    skip = run_terminal()
except Exception as e:
    print(f"Failed run_terminal: {e}")
