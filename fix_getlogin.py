import re

with open('fishing_game/game/ui/launcher.py', 'r') as f:
    content = f.read()

content = content.replace("username = os.getlogin() if hasattr(os, 'getlogin') else \"user\"", "try:\n        username = os.getlogin()\n    except:\n        username = \"user\"")

with open('fishing_game/game/ui/launcher.py', 'w') as f:
    f.write(content)
