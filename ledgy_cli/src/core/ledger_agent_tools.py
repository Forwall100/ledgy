from abc import ABC
from smolagents import Tool
from typing import List, Optional


class BaseLedgerTool(Tool, ABC):
    def __init__(self, ledger_instance, **kwargs):
        super().__init__(**kwargs)
        self.ledger_instance = ledger_instance

    def _execute_ledger(self, args: List[str]) -> str:
        """
        Выполняет команду ledger с обработкой ошибок.

        Args:
            args: Список аргументов команды

        Returns:
            Результат выполнения команды

        Raises:
            RuntimeError: При ошибке выполнения
        """
        try:
            return self.ledger_instance.execute(args)
        except Exception as e:
            raise RuntimeError(f"Ошибка выполнения ledger {args[0]}: {e}")


# ============================================================================
# БАЗОВЫЕ ИНСТРУМЕНТЫ
# ============================================================================


class LedgerBalanceTool(BaseLedgerTool):
    name = "ledger_balance"
    description = """
    Возвращает балансы счетов. Основной инструмент для анализа состояния счетов.
    
    Используй этот инструмент когда нужно:
    - Узнать текущий баланс конкретного счета или всех счетов
    - Увидеть иерархию счетов с балансами
    - Построить тренды (используй monthly=True для помесячной разбивки)
    
    Примеры использования:
    - Баланс всех счетов: ledger_balance()
    - Баланс расходов на еду: ledger_balance(account="expenses:food")
    """

    inputs = {
        "account": {
            "type": "string",
            "description": "Название счета или часть имени (опционально). Например: 'assets', 'expenses:food', 'income'",
            "nullable": True,
        },
        "period": {
            "type": "string",
            "description": "Период: 'thismonth', 'lastmonth', 'thisyear', '2024-Q3', '2024' и т.д. (опционально)",
            "nullable": True,
        },
        "depth": {
            "type": "integer",
            "description": "Глубина иерархии счетов (опционально, например: 2)",
            "nullable": True,
        },
        "monthly": {
            "type": "boolean",
            "description": "Группировать по месяцам для анализа трендов (опционально)",
            "nullable": True,
        },
        "weekly": {
            "type": "boolean",
            "description": "Группировать по неделям (опционально)",
            "nullable": True,
        },
        "daily": {
            "type": "boolean",
            "description": "Группировать по дням (опционально)",
            "nullable": True,
        },
    }
    output_type = "string"

    def forward(
        self,
        account: Optional[str] = None,
        period: Optional[str] = None,
        depth: Optional[int] = None,
        monthly: Optional[bool] = None,
        weekly: Optional[bool] = None,
        daily: Optional[bool] = None,
    ) -> str:
        args = ["bal"]

        if account:
            args.append(account)

        if period:
            args.extend(["--period", period])

        if depth is not None:
            args.extend(["--depth", str(depth)])

        if monthly:
            args.append("--monthly")
        elif weekly:
            args.append("--weekly")
        elif daily:
            args.append("--daily")

        return self._execute_ledger(args)


class LedgerRegisterTool(BaseLedgerTool):
    name = "ledger_register"
    description = """
    Возвращает регистр постингов (проводок) с бегущим балансом. Показывает детальную историю транзакций.
    
    Используй этот инструмент когда нужно:
    - Увидеть все транзакции по счету в хронологическом порядке
    - Отследить изменения баланса счета во времени
    - Найти конкретные транзакции
    - Проанализировать движения средств
    
    Примеры использования:
    - Все транзакции: ledger_register()
    - Транзакции по расходам на еду: ledger_register(account="expenses:food")
    - Помесячная сводка: ledger_register(account="income", monthly=True)
    """

    inputs = {
        "account": {
            "type": "string",
            "description": "Название счета (опционально)",
            "nullable": True,
        },
        "period": {
            "type": "string",
            "description": "Период (опционально)",
            "nullable": True,
        },
        "monthly": {
            "type": "boolean",
            "description": "Группировать по месяцам (опционально)",
            "nullable": True,
        },
        "weekly": {
            "type": "boolean",
            "description": "Группировать по неделям (опционально)",
            "nullable": True,
        },
        "daily": {
            "type": "boolean",
            "description": "Группировать по дням (опционально)",
            "nullable": True,
        },
    }
    output_type = "string"

    def forward(
        self,
        account: Optional[str] = None,
        period: Optional[str] = None,
        monthly: Optional[bool] = None,
        weekly: Optional[bool] = None,
        daily: Optional[bool] = None,
    ) -> str:
        args = ["reg"]

        if account:
            args.append(account)

        if period:
            args.extend(["--period", period])

        if monthly:
            args.append("--monthly")
        elif weekly:
            args.append("--weekly")
        elif daily:
            args.append("--daily")

        return self._execute_ledger(args)


class LedgerPrintTool(BaseLedgerTool):
    name = "ledger_print"
    description = """
    Возвращает полный текст транзакций в формате ledger.
    
    Используй этот инструмент когда нужно:
    - Увидеть полные транзакции с комментариями и тегами
    - Найти транзакции по описанию или получателю
    - Экспортировать данные
    - Проверить структуру транзакций
    
    Примеры использования:
    - Все транзакции: ledger_print()
    - Транзакции по счету: ledger_print(account="expenses:food")
    - Поиск по описанию: ledger_print(description="amazon")
    - За период: ledger_print(begin_date="2024-01-01", end_date="2024-12-31")
    """

    inputs = {
        "account": {
            "type": "string",
            "description": "Фильтр по счету (опционально)",
            "nullable": True,
        },
        "description": {
            "type": "string",
            "description": "Поиск по описанию транзакции (опционально)",
            "nullable": True,
        },
        "payee": {
            "type": "string",
            "description": "Поиск по получателю платежа (опционально)",
            "nullable": True,
        },
    }
    output_type = "string"

    def forward(
        self,
        account: Optional[str] = None,
        description: Optional[str] = None,
        payee: Optional[str] = None,
    ) -> str:
        args = ["print"]

        if account:
            args.append(account)

        if description:
            args.extend(["--limit", f"desc =~ /{description}/"])

        if payee:
            args.extend(["--limit", f"payee =~ /{payee}/"])

        return self._execute_ledger(args)


# ============================================================================
# СПРАВОЧНЫЕ ИНСТРУМЕНТЫ
# ============================================================================


class LedgerAccountsTool(BaseLedgerTool):
    name = "ledger_accounts"
    description = """
    Возвращает список всех счетов в журнале.
    
    Используй этот инструмент когда нужно:
    - Узнать какие счета существуют
    - Найти правильное название счета
    - Увидеть структуру счетов
    
    Примеры:
    - Все счета: ledger_accounts()
    - Счета расходов: ledger_accounts(pattern="expenses")
    - Подсчета первого уровня: ledger_accounts(depth=1)
    """

    inputs = {
        "pattern": {
            "type": "string",
            "description": "Паттерн для фильтрации счетов (опционально)",
            "nullable": True,
        },
        "depth": {
            "type": "integer",
            "description": "Глубина иерархии (опционально)",
            "nullable": True,
        },
    }
    output_type = "string"

    def forward(
        self,
        pattern: Optional[str] = None,
        depth: Optional[int] = None,
    ) -> str:
        args = ["accounts"]

        if pattern:
            args.append(pattern)

        if depth is not None:
            args.extend(["--depth", str(depth)])

        return self._execute_ledger(args)


class LedgerPayeesTool(BaseLedgerTool):
    name = "ledger_payees"
    description = """
    Возвращает список всех получателей платежей (payees).
    
    Используй этот инструмент когда нужно:
    - Узнать с кем/где были транзакции
    - Найти правильное написание получателя
    - Проанализировать частоту транзакций с конкретным получателем
    
    Примеры:
    - Все получатели: ledger_payees()
    - Поиск магазина: ledger_payees(pattern="amazon")
    """

    inputs = {
        "pattern": {
            "type": "string",
            "description": "Паттерн для поиска (опционально)",
            "nullable": True,
        },
    }
    output_type = "string"

    def forward(self, pattern: Optional[str] = None) -> str:
        args = ["payees"]

        if pattern:
            args.append(pattern)

        return self._execute_ledger(args)


class LedgerCommoditiesTool(BaseLedgerTool):
    name = "ledger_commodities"
    description = """
    Возвращает список всех используемых валют и товаров (commodities).
    
    Используй этот инструмент когда нужно:
    - Узнать какие валюты используются
    - Понять мультивалютную структуру
    - Найти инвестиционные позиции (акции, криптовалюты и т.д.)
    """

    inputs = {}
    output_type = "string"

    def forward(self) -> str:
        return self._execute_ledger(["commodities"])


class LedgerTagsTool(BaseLedgerTool):
    name = "ledger_tags"
    description = """
    Возвращает список всех тегов, используемых в транзакциях.
    
    Используй этот инструмент когда нужно:
    - Узнать какие теги используются для категоризации
    - Найти транзакции по проектам, поездкам и т.д.
    """

    inputs = {
        "pattern": {
            "type": "string",
            "description": "Паттерн для поиска тегов (опционально)",
            "nullable": True,
        },
    }
    output_type = "string"

    def forward(self, pattern: Optional[str] = None) -> str:
        args = ["tags"]

        if pattern:
            args.append(pattern)

        return self._execute_ledger(args)


# ============================================================================
# АНАЛИТИЧЕСКИЕ ИНСТРУМЕНТЫ
# ============================================================================


class LedgerStatsTool(BaseLedgerTool):
    name = "ledger_stats"
    description = """
    Возвращает статистику по журналу: количество транзакций, счетов, период данных.
    
    Используй этот инструмент когда нужно:
    - Получить общий обзор журнала
    - Узнать период покрытия данных
    - Понять объем данных
    """

    inputs = {
        "begin_date": {
            "type": "string",
            "description": "Начальная дата для статистики (опционально)",
            "nullable": True,
        },
        "end_date": {
            "type": "string",
            "description": "Конечная дата для статистики (опционально)",
            "nullable": True,
        },
    }
    output_type = "string"

    def forward(
        self,
        begin_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> str:
        args = ["stats"]

        if begin_date:
            args.extend(["--begin", begin_date])

        if end_date:
            args.extend(["--end", end_date])

        return self._execute_ledger(args)


def create_ledger_tools(ledger_instance) -> List[Tool]:
    return [
        # Базовые инструменты
        LedgerBalanceTool(ledger_instance),
        LedgerRegisterTool(ledger_instance),
        LedgerPrintTool(ledger_instance),
        # Справочные инструменты
        LedgerAccountsTool(ledger_instance),
        LedgerPayeesTool(ledger_instance),
        LedgerCommoditiesTool(ledger_instance),
        LedgerTagsTool(ledger_instance),
        # Аналитические инструменты
        LedgerStatsTool(ledger_instance),
    ]
