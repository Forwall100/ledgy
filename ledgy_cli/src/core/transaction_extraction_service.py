from datetime import date
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from ledgy_cli.src.extractors.factory import ExtractorFactory
from ledgy_cli.src.models.transaction import TransactionExtractionResult
from ledgy_cli.src.prompts.get_prompt import get_prompt
from ledgy_cli.src.utils.ledger import Ledger


class TransactionExtractionService:
    def __init__(
        self,
        base_url: str,
        api_key: SecretStr,
        vision_model: str,
        model: str,
        ledger_file_path: str,
        ledger_executable: str,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.vision_model = vision_model
        self.model = model
        self.ledger_file_path = ledger_file_path
        self.ledger_executable = ledger_executable

    def extract(
        self,
        input_data: str,
        default_currency: str,
        default_spending_account: str,
    ) -> TransactionExtractionResult:
        extractor = ExtractorFactory(
            self.base_url, self.api_key, self.vision_model
        ).create_extractor(input_data=input_data)

        content = extractor.extract_text(input_data=input_data)

        llm = ChatOpenAI(
            openai_api_base=self.base_url, api_key=self.api_key, model_name=self.model
        ).with_structured_output(TransactionExtractionResult)

        ledger = Ledger(
            ledger_file_path=self.ledger_file_path, base_command=self.ledger_executable
        )

        messages = [
            SystemMessage(
                content=get_prompt(
                    "SYSTEM",
                    existing_accounts=ledger.execute(["accounts"]),
                    current_date=date.today().strftime("%Y-%m-%d"),
                    default_currency=default_currency,
                    default_spending_account=default_spending_account,
                )
            ),
            HumanMessage(content=content),
        ]

        return TransactionExtractionResult.model_validate(llm.invoke(messages))
