from dataclasses import dataclass
from importlib import import_module
from os import listdir
from typing import Callable, List


@dataclass
class Module:
    page_func_name: str
    page_func: Callable[[], None]
    page_name: str
    page_desc: str
    page_visibility: bool


def get_all_modules(base_path: str) -> List[str]:
    return [x for x in listdir(base_path) if x.endswith(".py")]


def get_module_info(base_path: str, module_name: str) -> Module:
    module_obj = import_module(f"{base_path.split('/')[-1]}.{module_name}")
    page_func: Callable[[], None] = getattr(module_obj, module_name)  # 页面函数名与模块名相同
    page_name: str = getattr(module_obj, "NAME")
    page_desc: str = getattr(module_obj, "DESC")
    page_visibility: bool = getattr(module_obj, "VISIBILITY")

    return Module(
        page_func_name=module_name,
        page_func=page_func,
        page_name=page_name,
        page_desc=page_desc,
        page_visibility=page_visibility,
    )


def get_all_modules_info(base_path: str) -> List[Module]:
    return [
        get_module_info(base_path, x.split(".")[0]) for x in get_all_modules(base_path)
    ]
