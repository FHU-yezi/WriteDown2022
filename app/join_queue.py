from JianshuResearchTools.exceptions import InputError, ResourceError
from pywebio.output import put_markdown
from pywebio.pin import pin, put_input

from data.user import User, get_waiting_users_count
from utils.callback import bind_enter_key_callback
from utils.page import set_user_id_cookies
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

    set_user_id_cookies(user.id)

    toast_success("排队成功")


def join_queue() -> None:
    put_markdown(
        f"""
        # 排队

        为了降低服务器负载，我们会将用户的请求按顺序处理。

        您前面有 {get_waiting_users_count()} 位简友正在排队。
        """
    )

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
