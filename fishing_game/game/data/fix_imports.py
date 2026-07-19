import os
import re

def process_file(filename, added_imports):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Insert new imports at line index 2 (after the first couple of imports)
    for imp in reversed(added_imports):
        lines.insert(2, imp + "\n")
        
    content = "".join(lines)
    # Remove all indented 'import time', 'import random', 'import copy', 'import msvcrt'
    content = re.sub(r'^[ \t]+import (time|random|copy|msvcrt)\s*\n', '', content, flags=re.MULTILINE)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

process_file("main.py", [
    "import time",
    "import random",
    "try:\n    import msvcrt\nexcept ImportError:\n    msvcrt = None"
])

process_file("game/fishing.py", [
    "import copy"
])

process_file("game/shop.py", [
    "import time"
])

print("Imports fixed successfully.")
