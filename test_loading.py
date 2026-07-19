import sys
import time
import os
import random
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn, TimeRemainingColumn
from rich.align import Align
from rich.table import Table

console = Console()

def loading_screen_mock():
    text = "Good day, welcome to my fishing game. This project is my personal project and all credits belongs to me ultimately. Made by CruzXIIII."
    all_files = ["file1.py", "file2.py", "image.png", "data.json", "script.py", "module.py"] * 10

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

    layout["header"].update(Panel(Align.center(Text("FISHING GAME - INITIALIZATION SEQUENCE", style="bold cyan"))))

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        expand=True
    )
    task_id = progress.add_task("[cyan]Loading resources...", total=len(all_files))

    layout["footer"].update(Panel(progress, border_style="green"))

    intro_text = ""
    log_messages = []

    with Live(layout, refresh_per_second=20, console=console):
        text_idx = 0
        file_idx = 0
        while file_idx < len(all_files):
            # Advance text
            if text_idx < len(text):
                chars_to_add = max(1, len(text) // (len(all_files) // 2)) if file_idx > 0 else 1
                intro_text += text[text_idx:text_idx+chars_to_add]
                text_idx += chars_to_add

            # Advance file
            file = all_files[file_idx]
            log_messages.append(f"[green]Loaded[/green] {file}")
            if len(log_messages) > 10:
                log_messages.pop(0)

            progress.update(task_id, advance=1, description=f"[cyan]Loading {file}...")

            # Update panels
            intro_panel = Panel(Text(intro_text, justify="left", style="white"), title="[yellow]Message from Creator[/yellow]", border_style="blue")
            log_text = "\n".join(log_messages)
            log_panel = Panel(Text.from_markup(log_text), title="[magenta]System Log[/magenta]", border_style="magenta")

            layout["intro"].update(intro_panel)
            layout["log"].update(log_panel)

            time.sleep(0.05)
            file_idx += 1

        time.sleep(1)

loading_screen_mock()
