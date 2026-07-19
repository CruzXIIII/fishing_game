with open('fishing_game/game/ui/launcher.py', 'r') as f:
    content = f.read()

content = content.replace("if key in [b'\n', b'\n', b' ']:", "if key in [b'\\r', b'\\n', b' ']:")
content = content.replace("intro_text += \"\n\n[yellow]Initialization nearly complete...[/yellow]\n[gray]Press ENTER to skip.[/gray]\"", "intro_text += \"\\n\\n[yellow]Initialization nearly complete...[/yellow]\\n[gray]Press ENTER to skip.[/gray]\"")
content = content.replace("log_text = \"\n\".join(log_messages)", "log_text = \"\\n\".join(log_messages)")
content = content.replace("console.print(\"\n[bold green][+] System fully operational.[/bold green] 🚀\n\")", "console.print(\"\\n[bold green][+] System fully operational.[/bold green] 🚀\\n\")")

with open('fishing_game/game/ui/launcher.py', 'w') as f:
    f.write(content)
