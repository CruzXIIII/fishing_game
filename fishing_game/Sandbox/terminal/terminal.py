import platform
import os
import sys
import time
# pyrefly: ignore [missing-import]
from rich.console import Console
# pyrefly: ignore [missing-import]
from rich.table import Table
# pyrefly: ignore [missing-import]
from rich.progress import Progress, SpinnerColumn, TextColumn
# pyrefly: ignore [missing-import]
from rich.prompt import Prompt
from rich.markup import escape

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
        # escape brackets for rich markup!
        escaped_line = line.replace('[', '\\[').replace(']', '\\]')
        result.append(f'[{hex_color}]{escaped_line}[/]')
    return '\n'.join(result) + '\n'

DARK_BLUE = (0, 0, 139)
BRIGHT_BLUE = (0, 191, 255)

def terminal():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    console = Console()

    with Progress(
        SpinnerColumn(),
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
        username = os.getlogin() if hasattr(os, 'getlogin') else "user"
    except OSError:
        username = "user"
    hostname = platform.node()
    os_name = platform.system()
    kernel = platform.release()
    architecture = platform.machine()
    python_version = platform.python_version()

    stats_text = (
        f"[bold bright_magenta]╭──[/bold bright_magenta] [bold white]Cruz's Fishing Game 2.0[/bold white] [bold bright_magenta]───[/bold bright_magenta]\n"
        f"[bold bright_magenta]│[/bold bright_magenta] [bold cyan]USER:[/bold cyan]    [bold bright_yellow]{username}[/bold bright_yellow]@{hostname}\n"
        f"[bold bright_magenta]│[/bold bright_magenta] [bold cyan]HOST:[/bold cyan]    {os_name} [{architecture}]\n"
        f"[bold bright_magenta]│[/bold bright_magenta] [bold cyan]CORE:[/bold cyan]    Quantum Kernel v9.1.4\n"
        f"[bold bright_magenta]│[/bold bright_magenta] [bold cyan]LANG:[/bold cyan]    Python {python_version}\n"
        f"[bold bright_magenta]│[/bold bright_magenta] [bold cyan]STATUS:[/bold cyan]  [bold bright_green]ENCRYPTED & ONLINE[/bold bright_green]\n"
        f"[bold bright_magenta]╰───────────────────────────────[/bold bright_magenta]"
    )

    layout_table = Table.grid(padding=4)
    layout_table.add_column(no_wrap=True)
    layout_table.add_column(no_wrap=True)

    layout_table.add_row(ascii_logo, stats_text)

    console.print()
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
    console.print()

    while True:
        try:
            command = Prompt.ask(f"[bold bright_yellow]{username}[/bold bright_yellow]@[bold cyan]{hostname}[/bold cyan] >")
            cmd = command.strip().lower()
            if cmd in ('exit', 'quit'):
                break
            elif cmd:
                console.print(f"[red]Command not found:[/red] {escape(command)}")
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    terminal()