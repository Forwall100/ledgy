# Ledgy

Ledgy is a command-line interface (CLI) tool designed to help users manage their financial transactions and ledger entries. It provides functionalities to add transactions (including extraction from various sources) and ask questions about financial data. Ledgy integrates exclusively with `hledger` for its ledger management.

## Features
- **Add Transactions**: Add new financial transactions to your ledger. This includes the ability to extract transaction details from text, images, and documents.
- **Ask Questions**: Query your financial data using natural language to get insights and answers.

## Prerequisites

- **hledger**: Ledgy relies on `hledger` for all ledger operations. Please ensure `hledger` is installed and properly configured on your system. You can find installation instructions for `hledger` [here](https://hledger.org/install.html).

## Installation

To install Ledgy, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/ledgy.git
   cd ledgy
   ```

2. **Install Ledgy using uv**:
   ```bash
   uv tool install .
   ```

## Configuration

Ledgy uses a YAML configuration file located at `~/.config/ledgy/config.yaml` by default. If this file does not exist, Ledgy will create it with default values on its first run.

### Default Configuration (`~/.config/ledgy/config.yaml`)
```yaml
api:
  base_url: https://openrouter.ai/api/v1
  api_key: ""
  model: google/gemini-2.5-flash
  vision_model: google/gemini-2.5-flash
ledger:
  file_path: /home/user/.ledgy/bank.ledger # Default ledger file path
  executable: hledger # Ledgy works exclusively with 'hledger'
defaults:
  spending_account: Expenses:Unknown
  currency: RUB
```

## Usage

### 1. `add` command

Adds a new transaction to your ledger. This command is powerful as it can extract transaction details from various input types, including plain text, image files, and document files (PDF, TXT, DOCX).

```bash
ledgy add <input_data> [OPTIONS]
```

**Examples:**

- Add a simple transaction from a text string and print to console:
  ```bash
  ledgy add "2023/10/26 Groceries:Food  $50.00 Assets:Bank"
  ```

- Extract transactions from an image file and write to the default ledger file:
  ```bash
  ledgy add "/path/to/receipt.jpg" --write
  ```

- Extract transactions from a PDF document and write to a specific ledger file:
  ```bash
  ledgy add "/path/to/bank_statement.pdf" --file /path/to/my/personal.ledger --write
  ```

### 3. `serve` command

Starts a FastAPI server to expose `add` and `ask` functionalities via HTTP API.

```bash
ledgy serve [OPTIONS]
```

**Options:**
- `--host TEXT`: Host for the API server (default: `127.0.0.1`)
- `--port INTEGER`: Port for the API server (default: `8000`)

