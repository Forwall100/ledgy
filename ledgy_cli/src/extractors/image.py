import mimetypes
import base64
from pydantic import SecretStr
from ledgy_cli.src.extractors.base import BaseExtractor
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from ledgy_cli.src.prompts.get_prompt import get_prompt


def load_image_base64(path):
    mime_type, _ = mimetypes.guess_type(path)
    with open(path, "rb") as f:
        encoded_str = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded_str}"


class ImageExtractor(BaseExtractor):
    def __init__(self, base_url: str, api_key: SecretStr, model: str):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model

    def extract_text(self, input_data: str) -> str:
        v_llm = ChatOpenAI(
            openai_api_base=self.base_url, api_key=self.api_key, model_name=self.model
        )

        ocr_messages = [
            SystemMessage(content=get_prompt("OCR")),
            HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": "Распознай текст тут:",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": load_image_base64(input_data)},
                    },
                ]
            ),
        ]
        content = v_llm.invoke(ocr_messages).content

        if isinstance(content, str):
            return content
        else:
            raise RuntimeError(str(content))
