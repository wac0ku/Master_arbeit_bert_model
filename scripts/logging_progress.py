# logging_progress.py
from rich.progress import (
    Progress, BarColumn, TextColumn, 
    TimeRemainingColumn, MofNCompleteColumn,
    SpinnerColumn, ProgressColumn, TaskID
)
from rich.console import Console
from typing import Optional

console = Console()

class EASAProgress(Progress):
    """Custom Progress-Bar mit EASA-Standardformatierung"""
    def __init__(self):
        super().__init__(
            SpinnerColumn("dots", style="yellow"),
            TextColumn("[bold]{task.description}"),
            BarColumn(bar_width=40, complete_style="bright_blue", pulse_style="white"),
            MofNCompleteColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=True
        )

    def add_easa_task(self, description: str, total: int) -> TaskID:
        return self.add_task(
            f"[EASA] {description}",
            total=total,
            start=False
        )

def display_progress(iterable, description: str, **kwargs):
    """Kontextmanager für EASA-konforme Fortschrittsanzeige"""
    with EASAProgress() as progress:
        task = progress.add_easa_task(description, total=len(iterable))
        for item in iterable:
            yield item
            progress.update(task, advance=1)