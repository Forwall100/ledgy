import tempfile
import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, SecretStr
from typing import Optional

from ledgy_cli.src.core.ledger_agent_service import ask_ledger_agent
from ledgy_cli.src.core.transaction_extraction_service import (
    TransactionExtractionService,
)
from ledgy_cli.src.models.transaction import TransactionExtractionResult
from ledgy_cli.config import load_config
from ledgy_cli.src.utils.ledger import Ledger

app = FastAPI()

config = load_config()


class AskRequest(BaseModel):
    query: str


@app.post("/ask")
async def ask(request: AskRequest):
    api_model = config["api"]["model"]
    api_key = config["api"]["api_key"]
    api_base_url = config["api"]["base_url"]
    ledger_file_path = Path(config["ledger"]["file_path"]).expanduser()
    ledger_executable = config["ledger"]["executable"]

    if not api_key:
        raise HTTPException(status_code=500, detail="API key not set in config.yaml")

    try:
        result = ask_ledger_agent(
            query=request.query,
            api_model=api_model,
            api_key=api_key,
            api_base_url=api_base_url,
            ledger_file_path=str(ledger_file_path),
            ledger_executable=ledger_executable,
            verbose=True,
        )
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add")
async def add(
    text_content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    write: Optional[bool] = Form(False),
):
    api_key = config["api"]["api_key"]
    api_base_url = config["api"]["base_url"]
    vision_model = config["api"]["vision_model"]
    model = config["api"]["model"]
    ledger_file_path = Path(config["ledger"]["file_path"]).expanduser()
    ledger_executable = config["ledger"]["executable"]
    default_currency = config["defaults"]["currency"]
    default_spending_account = config["defaults"]["spending_account"]

    if not api_key:
        raise HTTPException(status_code=500, detail="API key not set in config.yaml")

    input_data = None
    tmp_file_path = None
    if file:
        # Создаем временный файл для хранения содержимого загруженного файла
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=file_extension
        ) as tmp_file:
            tmp_file.write(await file.read())
            tmp_file_path = tmp_file.name

        # Передаем путь к временному файлу
        input_data = tmp_file_path
    elif text_content:
        input_data = text_content

    if not input_data:
        raise HTTPException(
            status_code=400, detail="No content provided for adding transaction."
        )

    try:
        service = TransactionExtractionService(
            base_url=api_base_url,
            api_key=SecretStr(api_key),  # Wrap api_key in SecretStr
            vision_model=vision_model,
            model=model,
            ledger_file_path=str(ledger_file_path),
            ledger_executable=ledger_executable,
        )
        result: TransactionExtractionResult = service.extract(
            input_data=input_data,
            default_currency=default_currency,
            default_spending_account=default_spending_account,
        )

        # Если флаг write установлен, записываем транзакции в ledger файл
        if write:
            ledger = Ledger(str(ledger_file_path), base_command=ledger_executable)
            for transaction in result.final_answer:
                ledger.write_transaction(transaction)
            return {
                "message": f"Ledger entries written to {ledger_file_path}",
                "result": result.model_dump(),
            }
        else:
            return result.model_dump()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Удаляем временный файл, если он был создан
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                os.unlink(tmp_file_path)
            except Exception:
                pass  # Игнорируем ошибки удаления временного файла
