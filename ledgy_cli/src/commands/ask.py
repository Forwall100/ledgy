from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown

from ledgy_cli.config import load_config
from ledgy_cli.src.core.ledger_agent_service import ask_ledger_agent
from ledgy_cli.src.commands.common import validate_ledger_file_path

console = Console()


def ask(
    query: str,
    ledger_file: Optional[Path],
    config_path: Optional[Path],
    verbose: bool,
):
    config = load_config(config_path)

    actual_ledger_file_path = validate_ledger_file_path(
        ledger_file, config["ledger"]["file_path"]
    )
    if actual_ledger_file_path is None:
        return

    ledger_executable = config["ledger"]["executable"]

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    )
    progress.start()
    try:
        progress.add_task(description="Processing your query...", total=None)
        response = ask_ledger_agent(
            query,
            config["api"]["model"],
            config["api"]["api_key"],
            config["api"]["base_url"],
            str(actual_ledger_file_path),
            ledger_executable,
            verbose=verbose,
        )
    finally:
        progress.stop()
        progress.refresh()

    console.print(Panel(Markdown(response), border_style="green"))
