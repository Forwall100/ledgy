from ledgy_cli.src.extractors.base import BaseExtractor


class TextExtractor(BaseExtractor):
    def extract_text(self, input_data: str) -> str:
        return input_data
