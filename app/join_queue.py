from typing import Optional

from JianshuResearchTools.exceptions import InputError, ResourceError
from pywebio.output import put_info, put_markdown, put_success
from pywebio.pin import pin, put_input

from data.user import User, get_waiting_users_count
from utils.callback import bind_enter_key_callback
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
DESC: str = "查看统计数据前请先排队。"
VISIBILITY: bool = True


def on_submit_button_clicked() -> None:
    user_url: str = pin.user_url

    try:
        user = User.create(user_url)
    except (InputError, ResourceError):
        toast_warn_and_return("链接有误，请检查")

    set_user_slug_cookies(user.slug)

    toast_success("排队成功")


def on_clear_bind_data_button_clicked() -> None:
    remove_user_slug_cookies()
    toast_success("清除成功")
    reload(delay=1)


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
        user = User.from_slug(user_slug)

        if user.is_waiting or user.is_fetching:
            put_info(f"{user.name}，您已经在队列中了，数据正在全力获取中......")
        elif user.is_done or user.is_error:  # 错误信息在展示页面显示，因此出错时也让用户跳转到展示页面
            put_success(f"{user.name}，您的数据已经获取完成。")
            put_button(
                "点击查看>>",
                onclick=lambda: jump_to(
                    get_jump_link("display", query_args={"user_slug": user.slug})
                ),
                color="success",
                block=True,
            )

        put_button(
            "清除账号绑定信息",
            onclick=on_clear_bind_data_button_clicked,
            color="warning",
            block=True,
            outline=True,
        )

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

