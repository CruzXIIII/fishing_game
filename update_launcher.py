import sys

with open('fishing_game/game/ui/launcher.py', 'r') as f:
    content = f.read()

# We want to replace loading_screen with our rich implementation
import_block = """
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.prompt import Prompt
from rich.panel import Panel
from rich.layout import Layout
from rich.align import Align
from rich.status import Status
from rich.text import Text
from rich.markup import escape
from rich.live import Live
import threading
"""

content = content.replace(
"""
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.panel import Panel
from rich.layout import Layout
from rich.align import Align
from rich.status import Status
from rich.text import Text
from rich.markup import escape
""", import_block.strip() + "\n")

loading_func = """
def check_skip():
    if msvcrt and msvcrt.kbhit():
        key = msvcrt.getch()
        if key in [b'\\r', b'\\n', b' ']:
            return True
    return False

def check_skip_unix():
    import select
    i, o, e = select.select([sys.stdin], [], [], 0.0001)
    if i:
        sys.stdin.read(1)
        return True
    return False

def is_skip_pressed():
    if msvcrt:
        return check_skip()
    else:
        return check_skip_unix()

def loading_screen(skip):
    if skip:
        return

    console = Console()
    console.clear()

    text = "Good day, welcome to my fishing game. This project is my personal project and all credits belongs to me ultimately. Made by CruzXIIII."

    game_dir = os.path.dirname(os.path.abspath(__file__))
    all_files = []
    for root, dirs, files in os.walk(game_dir):
        for file in files:
            all_files.append(file)

    if not all_files:
        all_files = ["data.cpython-314.pyc"] * 50 # fallback

    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3)
    )

    layout["main"].split_row(
        Layout(name="intro", ratio=2),
        Layout(name="log", ratio=1)
    )

    header_text = Text("FISHING GAME - INITIALIZATION SEQUENCE", style="bold cyan")
    layout["header"].update(Panel(Align.center(header_text), border_style="blue"))

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None, style="dark_green", complete_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        expand=True
    )
    task_id = progress.add_task("[cyan]Loading resources...", total=len(all_files))

    layout["footer"].update(Panel(progress, border_style="green"))

    intro_text = ""
    log_messages = []

    # Non-blocking terminal setup for unix
    old_settings = None
    if not msvcrt:
        import termios
        import tty
        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            tty.setcbreak(fd)
        except:
            pass

    try:
        with Live(layout, refresh_per_second=20, console=console):
            text_idx = 0
            file_idx = 0
            skipped = False

            while file_idx < len(all_files):
                if is_skip_pressed():
                    skipped = True
                    break

                # Advance text
                if text_idx < len(text):
                    chars_to_add = max(1, len(text) // (len(all_files) // 2)) if file_idx > 0 else 1
                    intro_text += text[text_idx:text_idx+chars_to_add]
                    text_idx += chars_to_add
                elif text_idx >= len(text) and "..." not in intro_text:
                    intro_text += "\\n\\n[yellow]Initialization nearly complete...[/yellow]\\n[gray]Press ENTER to skip.[/gray]"

                # Advance file
                file = all_files[file_idx]
                log_messages.append(f"[green]Loaded[/green] {file}")
                if len(log_messages) > (console.size.height - 10):
                    log_messages.pop(0)

                progress.update(task_id, advance=1, description=f"[cyan]Loading {file}...")

                # Update panels
                intro_panel = Panel(Text.from_markup(intro_text), title="[bold yellow]Message from Creator[/bold yellow]", border_style="blue", padding=(1, 2))
                log_text = "\\n".join(log_messages)
                log_panel = Panel(Text.from_markup(log_text), title="[bold magenta]System Log[/bold magenta]", border_style="magenta")

                layout["intro"].update(intro_panel)
                layout["log"].update(log_panel)

                if winsound and file_idx % 3 == 0:
                    beep_async(600 + (file_idx % 5) * 50, 20)

                time.sleep(0.04)
                file_idx += 1

            if not skipped:
                # Fill remaining progress if needed
                progress.update(task_id, completed=len(all_files), description="[bold green]Loading complete![/bold green]")

                # Countdown phase
                for i in range(15, -1, -1):
                    if is_skip_pressed():
                        break

                    progress.update(task_id, description=f"[bold cyan]Opening game in {i/10:.1f} seconds...[/bold cyan]")

                    if winsound:
                        beep_async(1000 + i * 20, 50)
                    time.sleep(0.1)

    finally:
        if old_settings and not msvcrt:
            import termios
            try:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            except:
                pass

    console.clear()
    console.print("\\n[bold green][+] System fully operational.[/bold green] 🚀\\n")
    time.sleep(0.3)
"""

# Replace the original loading_screen function
import re
new_content = re.sub(r'def loading_screen\(skip\):.*?(?=\ndef run\(\):)', loading_func, content, flags=re.DOTALL)

with open('fishing_game/game/ui/launcher.py', 'w') as f:
    f.write(new_content)
