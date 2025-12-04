import mimetypes
from typing import cast
from pathlib import Path
from pydantic import SecretStr
from ledgy_cli.src.extractors.text import TextExtractor
from ledgy_cli.src.extractors.image import ImageExtractor
from ledgy_cli.src.extractors.document import DocumentExtractor


class ExtractorFactory:
    def __init__(self, base_url: str, api_key: SecretStr, vision_model: str):
        self.base_url = base_url
        self.api_key = api_key
        self.vision_model = vision_model

    def create_extractor(
        self, input_data: str
    ) -> ImageExtractor | DocumentExtractor | TextExtractor:
        if Path(input_data).exists():
            mime_type, _ = cast(str, mimetypes.guess_type(input_data))
            if mime_type and mime_type.startswith("image"):
                extractor = ImageExtractor(
                    base_url=self.base_url,
                    api_key=self.api_key,
                    model=self.vision_model,
                )
            else:
                extractor = DocumentExtractor()
        else:
            extractor = TextExtractor()

        return extractor
