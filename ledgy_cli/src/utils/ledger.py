import subprocess
from typing import Optional, List
import os
from ledgy_cli.src.models.transaction import Transaction


class Ledger:
    def __init__(self, ledger_file_path: str, base_command: str = "ledger"):
        self.ledger_file_path = os.path.abspath(ledger_file_path)
        self.base_command = base_command

        if not os.path.exists(self.ledger_file_path):
            raise FileNotFoundError(f"Ledger file not found: {self.ledger_file_path}")

    def execute(self, command_args: Optional[List[str]] = None) -> str:
        if command_args is None:
            command_args = []

        full_command = [self.base_command, "-f", self.ledger_file_path] + command_args

        try:
            result = subprocess.run(
                full_command, capture_output=True, text=True, timeout=300
            )

            if result.returncode == 0:
                return result.stdout
            else:
                error_msg = (
                    f"Ledger command failed with return code {result.returncode}"
                )
                if result.stderr:
                    error_msg += f": {result.stderr}"
                raise RuntimeError(error_msg)
        except Exception as e:
            raise RuntimeError(f"Error executing command: {str(e)}")

    def format_transaction(self, transaction: Transaction) -> str:
        transaction_string = f"{transaction.date} {transaction.description}\n"
        for posting in transaction.postings:
            transaction_string += f"    {posting.account}  "
            if posting.amount is not None and posting.currency is not None:
                transaction_string += f"{posting.amount:.2f} {posting.currency}"
            transaction_string += "\n"
        return transaction_string

    def write_transaction(self, transaction: Transaction):
        with open(self.ledger_file_path, "a") as f:
            f.write(self.format_transaction(transaction) + "\n")
