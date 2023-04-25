from typing import Any, Dict, Optional, Set

from pywebio.session import eval_js, info
from sspeedup.pywebio.cookies import get_cookies, remove_cookies, set_cookies
from sspeedup.pywebio.navigation import get_base_url

URL_SCHEME_ALLOW_LIST: Set[str] = {"Android", "iPhone", "iPad"}

def can_use_url_scheme() -> bool:
    ua: str = str(info.user_agent)

    return any(item in ua for item in URL_SCHEME_ALLOW_LIST)


def get_jump_link(module_name: str, query_args: Optional[Dict[str, Any]] = None) -> str:
    result = f"{get_base_url()}?app={module_name}"
    if not query_args:
        return result

    result += "&" + "&".join([f"{key}={value}" for key, value in query_args.items()])
    return result


def set_user_slug_cookies(user_slug: str) -> None:
    set_cookies({"user_slug": user_slug})


def get_user_slug_cookies() -> Optional[str]:
    return get_cookies().get("user_slug")

def remove_user_slug_cookies() -> None:
    remove_cookies()

def is_full_width() -> bool:
    return eval_js('$("#output-container")[0].clientWidth === 880')  # type: ignore
