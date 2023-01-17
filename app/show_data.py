from typing import Optional

from JianshuResearchTools.convert import UserUrlToUserSlug
from JianshuResearchTools.exceptions import InputError, ResourceError
from pywebio.output import put_markdown, toast, put_success
from pywebio.pin import pin, put_input

from data.user import User, get_waiting_users_count
from utils.exceptions import UserNotExistError
from utils.page import (
    get_jump_link,
    get_user_slug_cookies,
    jump_to,
    reload,
    remove_user_slug_cookies,
    set_user_slug_cookies,
)
from widgets.button import put_button
from widgets.toast import toast_success, toast_warn_and_return

NAME: str = "查看数据"
DESC: str = "查看数据获取状态，并跳转到结果页"
VISIBILITY: bool = True


def on_show_button_clicked() -> None:
    user_url: str = pin.user_url
    slug_from_cookie: Optional[str] = get_user_slug_cookies()
    if not user_url and not slug_from_cookie:
        toast_warn_and_return("请输入用户个人主页链接")

    try:
        user = (
            User.from_slug(UserUrlToUserSlug(user_url))
            if user_url
            else User.from_slug(slug_from_cookie)  # type: ignore [arg-type]
        )
    except (InputError, ResourceError):
        toast_warn_and_return("链接有误，请检查")
    except UserNotExistError:
        toast("您还没有排队，即将为您跳转到排队页面", color="warn")
        jump_to(get_jump_link("join_queue"), delay=1)
    else:
        if user_url and not slug_from_cookie:
            set_user_slug_cookies(UserUrlToUserSlug(user_url))

    if user.is_waiting_for_fetch or user.is_fetching:
        toast_warn_and_return("您的数据正在全力获取中，请稍等")

    toast_success("您的数据已经获取完成，即将为您跳转")
    jump_to(get_jump_link("display", {"user_slug": user.slug}), delay=1)


def on_clear_bind_data_button_clicked() -> None:
    remove_user_slug_cookies()
    toast_success("清除成功")
    reload(delay=1)


def show_data() -> None:
    user_slug: Optional[str] = get_user_slug_cookies()

    if not user_slug:
        put_input(
            "user_url",
            type="text",
            label="用户个人主页链接",
            placeholder="示例：https://www.jianshu.com/u/xxx",
        )
        put_button(
            "提交",
            onclick=on_show_button_clicked,
            color="success",
            block=True,
        )
        return

    try:
        user = User.from_slug(user_slug)
    except UserNotExistError:
        toast_success("用户身份信息无效，已自动清除")
        remove_user_slug_cookies()
        reload(delay=1)
        return

    if user.is_waiting_for_fetch or user.is_fetching:
        put_markdown(
            f"""
            我们正在全力获取您的数据，过一会再来试试吧。

            当前有 {get_waiting_users_count()} 人正在排队。
            """
        )
        return

    if user.is_error:
        put_markdown(
            f"""
            很抱歉，在获取数据的过程中出现了异常。

            错误信息：{user.error_info}
            """
        )
        return

    put_success(f"{user.name}，您的年度统计数据已经处理完毕。")
    put_button(
        "查看",
        onclick=on_show_button_clicked,
        color="success",
        block=True,
        outline=True,
    )

    put_button(
        "清除账号绑定信息",
        onclick=on_clear_bind_data_button_clicked,
        color="secondary",
        block=True,
        outline=True,
    )
