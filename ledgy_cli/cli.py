import typer
from pathlib import Path
from typing import Annotated, Optional

from ledgy_cli.src.commands.add import add as add_command
from ledgy_cli.src.commands.ask import ask as ask_command

app = typer.Typer(help="Ledgy CLI tool")


@app.command()
def add(
    input_data: str,
    ledger_file: Annotated[
        Optional[Path],
        typer.Option(
            "-f",
            "--file",
            help="Path to the ledger file.",
            exists=True,
            dir_okay=False,
            resolve_path=True,
        ),
    ] = None,
    write: Annotated[
        bool,
        typer.Option(
            "-w",
            "--write",
            help="Write the generated ledger entries to the ledger file.",
        ),
    ] = False,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output the result in JSON format.")
    ] = False,
    config_path: Annotated[
        Optional[Path],
        typer.Option(
            "--config",
            help="Path to an alternative configuration file.",
            exists=True,
            dir_okay=False,
            resolve_path=True,
        ),
    ] = None,
):
    """Add a new transaction"""
    add_command(
        input_data=input_data,
        ledger_file=ledger_file,
        write=write,
        json_output=json_output,
        config_path=config_path,
    )


@app.command()
def ask(
    query: str,
    ledger_file: Annotated[
        Optional[Path],
        typer.Option(
            "-f",
            "--file",
            help="Path to the ledger file.",
            exists=True,
            dir_okay=False,
            resolve_path=True,
        ),
    ] = None,
    config_path: Annotated[
        Optional[Path],
        typer.Option(
            "--config",
            help="Path to an alternative configuration file.",
            exists=True,
            dir_okay=False,
            resolve_path=True,
        ),
    ] = None,
    verbose: Annotated[
        bool, typer.Option("-v", "--verbose", help="Show all agent steps.")
    ] = False,
):
    """Ask questions about your ledger file"""
    ask_command(
        query=query, ledger_file=ledger_file, config_path=config_path, verbose=verbose
    )


if __name__ == "__main__":
    app()
