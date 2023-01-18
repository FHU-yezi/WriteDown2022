from typing import Optional
from utils.exceptions import UserNotExistError

from JianshuResearchTools.convert import UserUrlToUserSlug
from JianshuResearchTools.exceptions import InputError, ResourceError
from pywebio.output import put_info, put_markdown, put_success, toast
from pywebio.pin import pin, put_input

from data.user import User, get_waiting_users_count
from utils.callback import bind_enter_key_callback
from utils.exceptions import DuplicateUserError
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
        toast_warn_and_return("链接有误，请检查")
    except DuplicateUserError:
        # 用户已在数据库中
        # 写入 Cookie，以便在重载页面后隐藏排队提示
        set_user_slug_cookies(UserUrlToUserSlug(user_url))
        toast("您已经在队列中", color="warn")
        reload(delay=1)
        return

    # 排队成功，设置 Cookie 后刷新页面
    set_user_slug_cookies(user.slug)
    toast_success("排队成功")
    reload(delay=1)


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
        try:
            user = User.from_slug(user_slug)
        except UserNotExistError:
            # Cookie 中的 user_slug 无效或数据库被清空过
            # 清除对应信息后重载页面
            toast_success("本地缓存信息无效，已自动清除")
            remove_user_slug_cookies()
            reload(delay=1)
            return

        # 如果数据未获取完成，也未发生异常，提示正在获取中
        if not user.is_analyze_done and not user.is_error:
            put_info(f"{user.name}，您已经在队列中了，数据正在全力获取中......")

        # 数据获取完成或发生异常
        # 错误信息在展示页面显示，因此出错时也让用户跳转到展示页面
        elif user.is_analyze_done or user.is_error:
            put_success(f"{user.name}，您的数据已经获取完成。")
            put_button(
                "点击查看>>",
                onclick=lambda: jump_to(
                    get_jump_link(
                        "display",
                        query_args={"user_slug": user.slug},
                    )
                ),
                color="success",
                block=True,
            )

        put_button(
            "清除账号绑定信息",
            onclick=on_clear_bind_data_button_clicked,
            color="secondary",
            block=True,
            outline=True,
        )

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
