import os
import sys
from dataclasses import dataclass
from typing import Any, Optional

import yaml


@dataclass
class AppConfig:
    api_key: str
    api_host: str
    limit_message: Optional[int]
    limit_chars: Optional[int]
    temperature: float
    system_prompt: Optional[str] = None


def load_yaml_config(filepath: str = "final_project/config.yaml") -> dict[str, Any]:
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
    except Exception as e:
        print(f"Ошибка при чтении файла конфигурации {filepath}: {e}")
        return {}


def get_int_param(env_name: str, yaml_data: dict[str, Any], yaml_name: str) -> Optional[int]:
    val = os.environ.get(env_name)
    if val is not None:
        try:
            return int(val)
        except ValueError:
            print(f"Предупреждение: Переменная {env_name} должна быть числом.")

    yaml_val = yaml_data.get(yaml_name)
    if yaml_val is not None:
        try:
            return int(yaml_val)
        except ValueError:
            print(f"Предупреждение: Параметр {yaml_name} в YAML должен быть числом.")
    return None


def get_float_param(env_name: str, yaml_data: dict[str, Any], yaml_name: str, default: float) -> float:
    val = os.environ.get(env_name)
    if val is not None:
        try:
            return float(val)
        except ValueError:
            print(f"Предупреждение: Переменная {env_name} должна быть числом.")

    yaml_val = yaml_data.get(yaml_name)
    if yaml_val is not None:
        try:
            return float(yaml_val)
        except ValueError:
            print(f"Предупреждение: Параметр {yaml_name} в YAML должен быть числом.")
    return default


def setup_config() -> AppConfig:
    yaml_data = load_yaml_config()
    api_key = os.environ.get("API_KEY") or yaml_data.get("api_key")
    api_host = os.environ.get("API_HOST") or yaml_data.get("api_host")
    system_prompt = yaml_data.get("system_prompt")
    if not api_key or not api_host:
        print(
            "Критическая ошибка конфигурации:\n"
            "Не найдены параметры подключения (API_KEY, API_HOST).\n"
            "Задайте их через переменные окружения или создайте файл config.yaml."
        )
        sys.exit(1)
    limit_message = get_int_param("LIMIT_MESSAGE", yaml_data, "limit_message")
    limit_chars = get_int_param("LIMIT_CHARS", yaml_data, "limit_chars")
    temperature = get_float_param("TEMPERATURE", yaml_data, "temperature", default=0.7)
    if not (0.0 <= temperature <= 1.0):
        print("Предупреждение: Temperature должна быть в диапазоне [0, 1]. Сброс на 0.7.")
        temperature = 0.7
    return AppConfig(
        api_key=str(api_key),
        api_host=str(api_host),
        limit_message=limit_message,
        limit_chars=limit_chars,
        temperature=temperature,
        system_prompt=system_prompt or None,
    )
