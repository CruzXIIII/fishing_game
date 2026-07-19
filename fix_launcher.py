with open('fishing_game/game/ui/launcher.py', 'r') as f:
    content = f.read()

import re
content = re.sub(r'try:\n    try:\n        import winsound\n    except ImportError:\n        winsound = None\nexcept ImportError:\n    winsound = None', 'try:\n    import winsound\nexcept ImportError:\n    winsound = None', content)

with open('fishing_game/game/ui/launcher.py', 'w') as f:
    f.write(content)
