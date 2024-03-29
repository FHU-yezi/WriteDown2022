from os import path as os_path
from typing import Any, Dict

from yaml import safe_dump as yaml_dump
from yaml import safe_load as yaml_load

_DEFAULT_CONFIG = {
    "version": "v0.1.0",
    "base_path": "./app",
    "deploy": {
        "debug": False,
        "enable_PyWebIO_CDN": False,
        "PyWebIO_CDN": "",
        "PyEcharts_CDN": "",
        "port": 8080,
    },
    "queue_processor": {
        "check_interval": 10,
        "threads": 3,
    },
    "fetcher": {
        "sleep_interval_low": 0,
        "sleep_interval_high": 0,
    },
    "general_analyzer": {
        "analyze_interval": 3600,
    },
    "footer": "",
    "word_split_ability": {
        "host": "localhost",
        "port": 6001,
    },
    "db": {
        "host": "localhost",
        "port": 27017,
        "main_database": "WD2022Data",
    },
    "log": {
        "minimum_record_level": "DEBUG",
        "minimum_print_level": "INFO",
    },
}


class Config:
    def __new__(cls) -> "Config":
        # 单例模式
        if not hasattr(cls, "_instance"):
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not os_path.exists("config.yaml"):  # 没有配置文件
            with open("config.yaml", "w", encoding="utf-8") as f:
                yaml_dump(
                    _DEFAULT_CONFIG,
                    f,
                    allow_unicode=True,
                    indent=4,
                    sort_keys=False,
                )
            self._data = _DEFAULT_CONFIG
        else:  # 有配置文件
            with open("config.yaml", encoding="utf-8") as f:
                self._data = yaml_load(f)

    def __getattr__(self, name: str) -> Any:
        result: Any = self._data[name]
        if isinstance(result, dict):
            return ConfigNode(result)

        return result

    def refresh(self) -> None:
        self.__init__()


class ConfigNode:
    def __init__(self, data: Dict[str, Any]) -> None:
        self._data: Dict[str, Any] = data

    def __getattr__(self, name: str) -> Any:
        return self._data[name]


def init_config() -> Config:
    return Config()  # 初始化日志文件


config = init_config()
