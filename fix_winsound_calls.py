import os

files_to_fix = [
    'fishing_game/game/data/fishing.py',
    'fishing_game/game/data/shop.py'
]

for filepath in files_to_fix:
    with open(filepath, 'r') as f:
        content = f.read()

    # We just replace winsound.Beep( with if winsound: winsound.Beep(
    content = content.replace(" winsound.Beep(", " if winsound: winsound.Beep(")

    with open(filepath, 'w') as f:
        f.write(content)
