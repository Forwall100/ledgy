from markitdown import MarkItDown
from ledgy_cli.src.extractors.base import BaseExtractor


class DocumentExtractor(BaseExtractor):
    def extract_text(self, input_data: str) -> str:
        md = MarkItDown()
        return md.convert(input_data).text_content
