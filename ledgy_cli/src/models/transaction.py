from typing import List, Optional
from pydantic import BaseModel, Field


class OriginalAmount(BaseModel):
    amount: float = Field(
        ...,
        description="Исходная сумма в оригинальной валюте, если покупка была мультивалютной.",
    )
    currency: str = Field(..., description="Оригинальная валюта (например USD, EUR).")


class PriceLocal(BaseModel):
    amount: float = Field(
        ..., description="Локальная сумма после конвертации, если известна."
    )
    currency: str = Field(..., description="Локальная валюта (например RUB).")


class PostingConfidence(BaseModel):
    account: Optional[float] = Field(
        None, description="Уверенность в корректности выбранного счета (0.0–1.0)."
    )
    amount: Optional[float] = Field(
        None, description="Уверенность в корректности суммы (0.0–1.0)."
    )


class Posting(BaseModel):
    account: str = Field(
        ...,
        description=(
            "Название счета в формате Ledger, например "
            "'Assets:Bank:Sber', 'Expenses:Food:Coffee'. "
            "Это ключевая строка, соответствующая проводке."
        ),
    )

    amount: Optional[float] = Field(
        None,
        description=(
            "Сумма операции. Может отсутствовать у одной из строк, "
            "так как Ledger позволяет балансировать транзакцию автоматически. "
            "Суммы всегда положительные."
        ),
    )

    currency: Optional[str] = Field(
        None,
        description=(
            "Валюта суммы (например 'RUB', 'USD'). "
            "Если валюта не указана в тексте, используется default_currency."
        ),
    )

    original_amount: Optional[OriginalAmount] = Field(
        None,
        description="Оригинальная сумма (например в USD), если покупка была мультивалютной.",
    )

    confidence: Optional[PostingConfidence] = Field(
        None, description="Уровень уверенности по каждому компоненту проводки."
    )


# -------------------------------------------------------
# Описание одной транзакции (финальная операция)
# -------------------------------------------------------


class Transaction(BaseModel):
    date: str = Field(
        ...,
        description="Дата операции в формате YYYY-MM-DD. "
        "Если дата отсутствовала, используется текущая дата.",
    )

    description: str = Field(
        ..., description="Короткое описание транзакции, выводимое в ledger."
    )

    postings: List[Posting] = Field(
        ...,
        description=(
            "Список проводок (обычно минимум 2). "
            "Первая строка может быть категорией расходов/доходов, "
            "вторая — источником оплаты."
        ),
    )

    source_text_excerpt: Optional[str] = Field(
        None,
        description="Короткий фрагмент исходного текста, который был основой для этой транзакции.",
    )


# -------------------------------------------------------
# Структура полного ответа модели
# -------------------------------------------------------


class TransactionExtractionResult(BaseModel):
    determining_number_of_transactions: str = Field(
        ..., description="Краткое объяснение, как ты определил количество транзакций."
    )

    parsing_raw_text: str = Field(
        ...,
        description="Краткое формальное объяснение, как были извлечены сумма, валюта, дата.",
    )

    account_matching_logic: str = Field(
        ..., description="Объяснение, как был найден счет списания/зачисления."
    )

    category_deduction_logic: str = Field(
        ..., description="Почему выбрана конкретная категория или создана новая."
    )

    edge_cases_detected: str = Field(
        ...,
        description="Признаки ошибок входных данных, неоднозначностей, OCR-шума, "
        "неточностей или пустых значений. "
        "Если всё корректно — 'Нет'.",
    )

    final_answer: List[Transaction] = Field(
        ...,
        description="Список итоговых транзакций, полностью готовых для записи в Ledger файл.",
    )
