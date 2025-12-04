from pydantic import SecretStr
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ledgy_cli.src.core.transaction_extraction_service import (
    TransactionExtractionService,
)
from ledgy_cli.src.utils.ledger import Ledger
from ledgy_cli.config import load_config
from ledgy_cli.src.commands.common import validate_ledger_file_path

console = Console()


def add(
    input_data: str,
    ledger_file: Optional[Path],
    write: bool,
    json_output: bool,
    config_path: Optional[Path],
):
    config = load_config(config_path)

    actual_ledger_file_path = validate_ledger_file_path(
        ledger_file, config["ledger"]["file_path"]
    )
    if actual_ledger_file_path is None:
        return

    service = TransactionExtractionService(
        base_url=config["api"]["base_url"],
        api_key=SecretStr(config["api"]["api_key"]),
        vision_model=config["api"]["vision_model"],
        model=config["api"]["model"],
        ledger_executable=config["ledger"]["executable"],
        ledger_file_path=str(actual_ledger_file_path),
    )

    # Show spinner while extracting transactions
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    )
    progress.start()
    try:
        progress.add_task(description="Extracting transactions...", total=None)
        result = service.extract(
            input_data=input_data,
            default_currency=config["defaults"]["currency"],
            default_spending_account=config["defaults"]["spending_account"],
        )
    finally:
        progress.stop()

    if json_output:
        typer.echo(result.model_dump_json(indent=2))
    else:
        ledger = Ledger(
            str(actual_ledger_file_path), base_command=config["ledger"]["executable"]
        )
        output_content = ""
        for transaction in result.final_answer:
            output_content += ledger.format_transaction(transaction) + "\n"

        if write:
            # Show spinner while writing transactions
            write_progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            )
            write_progress.start()
            try:
                write_progress.add_task(
                    description="Writing transactions to ledger...", total=None
                )
                for transaction in result.final_answer:
                    ledger.write_transaction(transaction)
            finally:
                write_progress.stop()
                write_progress.refresh()

            console.print(f"✅ Ledger entries written to {actual_ledger_file_path}")
        else:
            console.print(output_content)
