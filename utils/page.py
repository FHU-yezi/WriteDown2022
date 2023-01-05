from typing import Dict, Optional, Set, Union

from pywebio.session import eval_js, info, run_js

URL_SCHEME_ALLOW_LIST: Set[str] = {"Android", "iPhone", "iPad"}


def set_footer(html: str) -> None:
    run_js(f"$('footer').html('{html}')")


def jump_to(url: str, new_window: bool = False) -> None:
    run_js(f'window.open("{url}", "{"_blank" if new_window else "_target"}")')


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


def can_use_URL_Scheme() -> bool:
    ua: str = str(info.user_agent)

    for item in URL_SCHEME_ALLOW_LIST:
        if item in ua:
            return True

    return False


def get_base_url() -> str:
    return eval_js(
        'window.location.href.split("?")[0]'
        '.replace(window.pathname != "/" ? window.pathname : "", "")'
    )


def get_jump_link(module_name: str, query_args: Optional[Dict] = None) -> str:
    result = f"{get_base_url()}?app={module_name}"
    if not query_args:
        return result

    result += "&" + "&".join([f"{key}={value}" for key, value in query_args.items()])
    return result


def set_cookies(data: Dict[str, Union[str, int, float]]) -> None:
    cookies_str = ";".join([f"{key}={value}" for key, value in data.items()])
    run_js(f"document.cookie = {cookies_str}")


def get_cookies() -> Dict[str, str]:
    cookies_str: str = eval_js("document.cookie")
    if not cookies_str:  # Cookie 字符串为空
        return {}

    return dict([x.split("=") for x in cookies_str.split("; ")])


def set_user_slug_cookies(user_slug: str) -> None:
    set_cookies({"user_slug": user_slug})


def get_user_slug_cookies() -> Optional[str]:
    return get_cookies().get("user_slug")


def get_query_params() -> Dict[str, str]:
    url = eval_js("window.location.href")
    result: Dict[str, str] = dict([x.split("=") for x in url.split("?")[1].split("&")])
    if result.get("app"):  # 去除子页面参数
        del result["app"]
    return result
