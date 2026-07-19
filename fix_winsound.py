import os

for root, _, files in os.walk('fishing_game'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as f:
                content = f.read()
            if 'import winsound' in content:
                content = content.replace('import winsound', 'try:\n    import winsound\nexcept ImportError:\n    winsound = None')
                # deduplicate if it was already wrapped but maybe messed up
                content = content.replace('try:\n    try:\n        import winsound\n    except ImportError:\n        winsound = None\nexcept ImportError:\n    winsound = None', 'try:\n    import winsound\nexcept ImportError:\n    winsound = None')
                with open(filepath, 'w') as f:
                    f.write(content)
