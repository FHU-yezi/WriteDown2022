from typing import Optional

from JianshuResearchTools.convert import UserUrlToUserSlug
from JianshuResearchTools.exceptions import InputError, ResourceError
from pywebio.output import put_markdown
from pywebio.pin import pin, put_input

from data.user import User, get_waiting_users_count
from utils.callback import bind_enter_key_callback
from utils.exceptions import DuplicateUserError, UserNotExistError
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

NAME: str = "排队"
DESC: str = "查看统计数据前请先排队"
VISIBILITY: bool = True


def on_submit_button_clicked() -> None:
    user_url: str = pin.user_url

    try:
        user = User.create(user_url)
    except (InputError, ResourceError):
        toast_warn_and_return("输入的链接无效，请检查")
    except DuplicateUserError:
        # 用户已在数据库中，设置 Cookie 后跳转到查看结果页面
        set_user_slug_cookies(UserUrlToUserSlug(user_url))

        toast_success("您已排队，即将跳转到查看结果页面")
        jump_to(get_jump_link("show_data"), delay=1)
        return
    else:
        # 排队成功，设置 Cookie 后跳转到查看结果页面
        set_user_slug_cookies(user.slug)
        toast_success("排队成功")
        jump_to(get_jump_link("show_data"), delay=1)


def join_queue() -> None:
    put_markdown(
        f"""
        # 排队

        为了降低服务器负载，我们会将用户的请求按顺序处理。

        您前面有 {get_waiting_users_count()} 位简友正在排队。
        """
    )

    user_slug: Optional[str] = get_user_slug_cookies()
    if user_slug:
        try:
            User.from_slug(user_slug)
        except UserNotExistError:
            # Cookie 中的 user_slug 无效或数据库被清空过
            # 清除对应信息后重载页面
            toast_success("已清除无效的本地信息")
            remove_user_slug_cookies()
            reload(delay=1)
            return
        else:
            # 用户已经排队过，跳转到查看结果页面
            toast_success("您已排队，即将跳转到查看结果页面")
            jump_to(get_jump_link("show_data"), delay=1)
            return

    # 没有 user_slug 信息，提示排队
    else:
        put_input(
            "user_url",
            type="text",
            label="用户个人主页链接",
            placeholder="示例：https://www.jianshu.com/u/xxx",
        )
        put_button(
            "提交",
            onclick=on_submit_button_clicked,
            color="success",
            block=True,
        )

        bind_enter_key_callback(
            "user_url",
            on_press=lambda _: on_submit_button_clicked(),
        )
