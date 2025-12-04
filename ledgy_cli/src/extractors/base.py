from abc import ABC, abstractmethod
from typing import Any


class BaseExtractor(ABC):
    @abstractmethod
    def extract_text(self, input_data: Any) -> str:
        pass
