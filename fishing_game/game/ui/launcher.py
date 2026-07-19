import sys
import time
import os
import platform
import random
import threading

try:
    import winsound
except ImportError:
    winsound = None

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.live import Live
from rich.prompt import Prompt
from rich.panel import Panel
from rich.layout import Layout
from rich.align import Align
from rich.status import Status
from rich.text import Text
from rich.markup import escape

try:
    import msvcrt
except ImportError:
    msvcrt = None
os.system("") # Enable ANSI escape codes on Windows

# Add root directory to path to ensure imports work
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from game.ui.main import main as start_game

# Helpers from terminal.py
def interpolate_color(color_start, color_end, factor):
    r = int(color_start[0] + (color_end[0] - color_start[0]) * factor)
    g = int(color_start[1] + (color_end[1] - color_start[1]) * factor)
    b = int(color_start[2] + (color_end[2] - color_start[2]) * factor)
    return f'#{r:02X}{g:02X}{b:02X}'

def apply_line_gradient(text, color_start, color_end):
    lines = text.splitlines()
    num_lines = max(1, len(lines) - 1)
    result = []
    for i, line in enumerate(lines):
        factor = i / num_lines
        hex_color = interpolate_color(color_start, color_end, factor)
        escaped_line = line.replace('[', '\\[').replace(']', '\\]')
        result.append(f'[{hex_color}]{escaped_line}[/]')
    return '\n'.join(result) + '\n'

DARK_BLUE = (0, 0, 139)
BRIGHT_BLUE = (0, 191, 255)

def run_terminal():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    console = Console()
    console.clear()

    with Progress(
        SpinnerColumn(spinner_name="bouncingBar"),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Connecting to server...", total=None)
        time.sleep(0.6)
        progress.update(task, description="[magenta]Decrypting modules...")
        time.sleep(0.8)
        progress.update(task, description="[green]Loading Fishing Engine...")
        time.sleep(1.0)

    fish_art = (
        "  ______ _____  _____ _    _ \n"
        " |  ____|_   _|/ ____| |  | |\n"
        " | |__    | | | (___ | |__| |\n"
        " |  __|   | |  \\___ \\|  __  |\n"
        " | |     _| |_ ____) | |  | |\n"
        " |_|    |_____|_____/|_|  |_|"
    )
    ascii_logo = apply_line_gradient(fish_art, DARK_BLUE, BRIGHT_BLUE)

    try:
        username = os.getlogin()
    except:
        username = "user"
    hostname = platform.node()
    os_name = platform.system()
    architecture = platform.machine()
    python_version = platform.python_version()

    stats_table = Table.grid(padding=1)
    stats_table.add_column(style="cyan", justify="left")
    stats_table.add_column(style="white", justify="left")
    
    stats_table.add_row("USER:", f"[bold bright_yellow]{username}[/bold bright_yellow]@{hostname}")
    stats_table.add_row("HOST:", f"{os_name} [{architecture}]")
    stats_table.add_row("CORE:", "Quantum Kernel v9.1.4")
    stats_table.add_row("LANG:", f"Python {python_version}")
    stats_table.add_row("STATUS:", "[bold bright_green]ENCRYPTED & ONLINE[/bold bright_green]")

    stats_panel = Panel(
        stats_table, 
        title="[bold yellow]System Info[/bold yellow]", 
        border_style="bright_magenta",
        expand=False
    )

    layout_table = Table.grid(padding=4)
    layout_table.add_column(no_wrap=True)
    layout_table.add_column(no_wrap=True)
    layout_table.add_row(ascii_logo, stats_panel)

    console.print(layout_table)
    console.print()

    color_block = "████"
    palette = (
        f"[black]{color_block}[/black]"
        f"[red]{color_block}[/red]"
        f"[green]{color_block}[/green]"
        f"[yellow]{color_block}[/yellow]"
        f"[blue]{color_block}[/blue]"
        f"[magenta]{color_block}[/magenta]"
        f"[cyan]{color_block}[/cyan]"
        f"[white]{color_block}[/white]"
    )
    console.print(f"   {palette}")
    console.print("\nType [green]'python execute'[/green] to start.")

    while True:
        try:
            command = Prompt.ask(f"[bold bright_yellow]{username}[/bold bright_yellow]@[bold cyan]{hostname}[/bold cyan] >")
            cmd = command.strip().lower()
            if cmd == 'python execute':
                console.print("[green]Very well.[/green]\n")
                if winsound: winsound.Beep(1000, 500)
                time.sleep(1.0)
                return False # Don't skip loading
            elif cmd == 'cruzskip':
                return True # Skip loading
            elif cmd in ('exit', 'quit'):
                sys.exit(0)
            elif cmd:
                console.print(f"[red]Command not found:[/red] {escape(command)}")
                if winsound: winsound.Beep(200, 300)
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)

def beep_async(freq, duration):
    if winsound:
        threading.Thread(target=winsound.Beep, args=(freq, duration), daemon=True).start()

def check_skip():
    if msvcrt and msvcrt.kbhit():
        key = msvcrt.getch()
        if key in [b'\r', b'\n', b' ']:
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
        all_files = ["data.cpython-314.pyc"] * 50

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

                if text_idx < len(text):
                    chars_to_add = max(1, len(text) // (len(all_files) // 2)) if file_idx > 0 else 1
                    intro_text += text[text_idx:text_idx+chars_to_add]
                    text_idx += chars_to_add
                elif text_idx >= len(text) and "..." not in intro_text:
                    intro_text += "\n\n[yellow]Initialization nearly complete...[/yellow]\n[gray]Press ENTER to skip.[/gray]"

                file = all_files[file_idx]
                log_messages.append(f"[green]Loaded[/green] {file}")
                if len(log_messages) > (console.size.height - 10):
                    log_messages.pop(0)

                progress.update(task_id, advance=1, description=f"[cyan]Loading {file}...")

                intro_panel = Panel(Text.from_markup(intro_text), title="[bold yellow]Message from Creator[/bold yellow]", border_style="blue", padding=(1, 2))
                log_text = "\n".join(log_messages)
                log_panel = Panel(Text.from_markup(log_text), title="[bold magenta]System Log[/bold magenta]", border_style="magenta")

                layout["intro"].update(intro_panel)
                layout["log"].update(log_panel)

                if winsound and file_idx % 3 == 0:
                    beep_async(600 + (file_idx % 5) * 50, 20)

                time.sleep(0.04)
                file_idx += 1

            if not skipped:
                progress.update(task_id, completed=len(all_files), description="[bold green]Loading complete![/bold green]")

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
    console.print("\n[bold green][+] System fully operational.[/bold green] 🚀\n")
    time.sleep(0.3)


def run():
    skip = run_terminal()
    loading_screen(skip)
    start_game()

if __name__ == "__main__":
    run()
