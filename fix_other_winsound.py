import os

files_to_fix = [
    'fishing_game/game/ui/main.py',
    'fishing_game/game/data/fishing.py',
    'fishing_game/game/data/shop.py',
    'fishing_game/game/ui/beforelaunch.py'
]

for filepath in files_to_fix:
    with open(filepath, 'r') as f:
        content = f.read()

    if filepath == 'fishing_game/game/ui/beforelaunch.py':
        continue # beforelaunch already handles winsound manually or we will fix it if needed

    # Replace import winsound exactly at line start
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line == 'import winsound':
            lines[i] = 'try:\n    import winsound\nexcept ImportError:\n    pass'

    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))
