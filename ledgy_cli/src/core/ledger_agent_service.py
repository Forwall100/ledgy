from smolagents import CodeAgent, OpenAIModel, LogLevel
from ledgy_cli.src.utils.ledger import Ledger
from ledgy_cli.src.prompts.get_prompt import get_prompt
from typing import cast
from ledgy_cli.src.core.ledger_agent_tools import create_ledger_tools


def create_ledger_agent(
    api_model: str,
    api_key: str,
    api_base_url: str,
    ledger_file_path: str,
    ledger_executable: str,
    verbose: bool,
):
    llm = OpenAIModel(
        temperature=0,
        model_id=api_model,
        api_key=api_key,
        api_base=api_base_url,
    )

    # Create ledger instance and configured tools
    ledger_instance = Ledger(ledger_file_path, base_command=ledger_executable)
    tools = create_ledger_tools(ledger_instance)

    if not verbose:
        agent = CodeAgent(
            tools=tools,
            model=llm,
            additional_authorized_imports=["pandas", "math", "random", "numpy"],
            verbosity_level=LogLevel.ERROR,
            max_steps=10,
        )
    else:
        agent = CodeAgent(
            tools=tools,
            model=llm,
            additional_authorized_imports=["pandas", "math", "random", "numpy"],
            max_steps=10,
        )

    return agent


def ask_ledger_agent(
    query: str,
    api_model: str,
    api_key: str,
    api_base_url: str,
    ledger_file_path: str,
    ledger_executable: str,
    verbose: bool = False,
) -> str:
    agent = create_ledger_agent(
        api_model, api_key, api_base_url, ledger_file_path, ledger_executable, verbose
    )
    system_prompt = get_prompt("AGENT_SYSTEM")

    result = agent.run(f"""
{system_prompt}

---

Запрос пользователя:
{query}
    """)
    return cast(str, result)
