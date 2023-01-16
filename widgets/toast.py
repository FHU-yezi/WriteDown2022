from functools import partial
from typing import Callable, NoReturn

from pywebio.output import toast


def toast_warn_and_return(text: str) -> NoReturn:
    toast(text, color="warn")
    exit()


def toast_error_and_return(text: str) -> NoReturn:
    toast(text, color="error")
    exit()


toast_success: Callable = partial(toast, color="success")
