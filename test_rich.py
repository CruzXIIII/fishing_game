import time
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, SpinnerColumn
from rich.layout import Layout
from rich.console import Group
from rich.text import Text

def make_layout():
    layout = Layout(name="root")
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3)
    )
    layout["main"].split_row(
        Layout(name="left", ratio=2),
        Layout(name="right", ratio=1)
    )
    return layout

progress = Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    TimeRemainingColumn(),
)
task_id = progress.add_task("Loading Files...", total=100)

layout = make_layout()
layout["header"].update(Panel(Text("FISHING GAME INITIALIZATION", justify="center", style="bold cyan")))
layout["footer"].update(Panel(progress))

with Live(layout, refresh_per_second=10):
    for i in range(100):
        progress.update(task_id, advance=1)
        time.sleep(0.05)
