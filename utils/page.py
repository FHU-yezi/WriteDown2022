from time import sleep
from typing import Dict, Optional, Set, Union

from pywebio.session import eval_js, info, run_js

URL_SCHEME_ALLOW_LIST: Set[str] = {"Android", "iPhone", "iPad"}


def set_footer(html: str) -> None:
    run_js(f"$('footer').html('{html}')")


def jump_to(url: str, new_window: bool = False, delay: int = 0) -> None:
    if delay:
        sleep(delay)
    run_js(f'window.open("{url}", "{"_blank" if new_window else "_self"}")')


def get_current_link() -> str:
    return eval_js("window.location.href")  # type: ignore


def copy_to_clipboard(text: str) -> None:
    # 参见：https://juejin.cn/post/7119169721081004069
    run_js(
        """
        const copyDom = document.createElement("textarea");
        copyDom.value = "%s";
        document.body.appendChild(copyDom);
        setTimeout(() => {
            copyDom.select();
            document.execCommand("Copy");
            document.body.removeChild(copyDom);
        }, 100);
        """
        % text
    )


def can_use_url_scheme() -> bool:
    ua: str = str(info.user_agent)

    return any(item in ua for item in URL_SCHEME_ALLOW_LIST)


def get_base_url() -> str:
    return eval_js(
        'window.location.href.split("?")[0]'
        '.replace(window.pathname != "/" ? window.pathname : "", "")'
    )  # type: ignore


def reload(delay: int = 0) -> None:
    if delay:
        sleep(delay)
    run_js("location.reload()")


def get_jump_link(module_name: str, query_args: Optional[Dict] = None) -> str:
    result = f"{get_base_url()}?app={module_name}"
    if not query_args:
        return result

    result += "&" + "&".join([f"{key}={value}" for key, value in query_args.items()])
    return result


def set_cookies(data: Dict[str, Union[str, int, float]]) -> None:
    cookies_str = ";".join([f"{key}={value}" for key, value in data.items()])
    run_js(f"document.cookie = '{cookies_str}'")


def get_cookies() -> Dict[str, str]:
    cookies_str: str = eval_js("document.cookie")  # type: ignore
    if not cookies_str:  # Cookie 字符串为空
        return {}

    return dict([x.split("=") for x in cookies_str.split("; ")])


def remove_cookies(key: str) -> None:
    run_js(f"document.cookie = '{key}='")


def set_user_slug_cookies(user_slug: str) -> None:
    set_cookies({"user_slug": user_slug})


def get_user_slug_cookies() -> Optional[str]:
    return get_cookies().get("user_slug")


def remove_user_slug_cookies() -> None:
    remove_cookies("user_slug")


def get_query_params() -> Dict[str, str]:
    url = eval_js("window.location.href")
    result: Dict[str, str] = dict(
        [x.split("=") for x in url.split("?")[1].split("&")],  # type: ignore
    )
    if result.get("app"):  # 去除子页面参数
        del result["app"]
    return result


def is_full_width() -> bool:
    return eval_js('$("#output-container")[0].clientWidth === 880')  # type: ignore
