import os
from typing import Any


def get_prompt(prompt_name: str, **kwargs: Any) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, f"{prompt_name}.md")

    if not os.path.exists(prompt_path):
        raise FileNotFoundError(
            f"Промпт файл '{prompt_path}' не найден в директории модуля"
        )

    try:
        with open(prompt_path, "r", encoding="utf-8") as file:
            prompt_content = file.read()

        # Форматируем промпт с переданными параметрами
        formatted_prompt = prompt_content.format(**kwargs)

        return formatted_prompt

    except KeyError as e:
        raise KeyError(f"Не передано значение для плейсхолдера: {e}")
    except Exception as e:
        raise Exception(
            f"Ошибка при чтении или форматировании файла '{prompt_path}': {str(e)}"
        )
