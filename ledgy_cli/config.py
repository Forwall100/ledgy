import yaml
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "ledgy"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.yaml"

DEFAULT_CONFIG = {
    "api": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": "",
        "model": "google/gemini-2.5-flash",
        "vision_model": "google/gemini-2.5-flash",
    },
    "ledger": {
        "file_path": str(Path.home() / ".ledgy" / "bank.ledger"),
        "executable": "hledger",
    },
    "defaults": {
        "spending_account": "Expenses:Unknown",
        "currency": "RUB",
    },
}


def get_config_path(config_path=None):
    if config_path:
        return Path(config_path)
    return DEFAULT_CONFIG_FILE


def load_config(config_path=None):
    config_file = get_config_path(config_path)

    if not config_file.exists():
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, "w") as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)
        return DEFAULT_CONFIG

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    merged_config = DEFAULT_CONFIG.copy()
    _deep_merge(merged_config, config)
    return merged_config


def _deep_merge(base, new):
    for k, v in new.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


def save_config(config, config_path=None):
    config_file = get_config_path(config_path)
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, "w") as f:
        yaml.dump(config, f, default_flow_style=False)


def get_setting(section, key, config=None, config_path=None):
    if config is None:
        config = load_config(config_path)
    return config.get(section, {}).get(key)


def set_setting(section, key, value, config_path=None):
    config = load_config(config_path)
    if section not in config:
        config[section] = {}
    config[section][key] = value
    save_config(config, config_path)
