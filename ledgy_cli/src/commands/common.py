from pathlib import Path
import typer
from typing import Optional


def validate_ledger_file_path(
    ledger_file: Optional[Path], default_ledger_file_path: str
) -> Optional[Path]:
    """
    Валидирует путь к ledger-файлу.
    """
    if ledger_file:
        actual_ledger_file_path = ledger_file.expanduser()
    else:
        actual_ledger_file_path = Path(default_ledger_file_path).expanduser()

    if not actual_ledger_file_path.exists():
        typer.echo(
            f"Error: Ledger file not found at {actual_ledger_file_path}. "
            "Please ensure the file exists and the path is correct, or configure it in config.yaml.",
            err=True,
        )
        return None
    if not actual_ledger_file_path.is_file():
        typer.echo(
            f"Error: Path {actual_ledger_file_path} is not a file. "
            "Please specify a valid ledger file.",
            err=True,
        )
        return None

    return actual_ledger_file_path
