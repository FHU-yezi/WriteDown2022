from typing import Optional

from pywebio.output import put_html, put_markdown, put_row
from pywebio.pin import put_input

from data.user import User, get_waiting_users_count
from utils.html import grey_text
from utils.page import (
    copy_to_clipboard,
    get_current_link,
    get_jump_link,
    get_query_params,
    get_user_slug_cookies,
    jump_to,
)
from widgets.button import put_button
from widgets.toast import toast_error_and_return, toast_success

NAME: str = "数据展示"
DESC: str = "查看您的年度统计数据"
VISIBILITY: bool = False


def on_copy_link_button_clicked(current_link: str) -> None:
    copy_to_clipboard(current_link)
    toast_success("复制成功")


def display() -> None:
    user_slug_from_query_arg = get_query_params().get("user_slug")
    if not user_slug_from_query_arg:
        toast_error_and_return("请求参数错误")

    try:
        user = User.from_slug(user_slug_from_query_arg)
    except ValueError:
        toast_error_and_return("请求参数错误")

    if user.is_waiting or user.is_fetching:
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
            很抱歉，在获取数据的过程中发生了异常。

            错误信息：{user.error_info}
            """
        )
        return

    user.result_shown()

    put_markdown(
        f"""
        # {user.name} 的 2022 年度数据统计

        {grey_text(
            f'生成时间：{user.end_fetch_time.strftime(r"%Y-%m-%d %H:%M:%S")} | '
            f'展示次数：{user.result_show_count}'
        )}
        """
    )

    put_markdown(user.interaction_summary.get_summary(), sanitize=False)

    put_html(user.heat_graph.get_graph_obj().render_notebook())

    put_html(user.interaction_type_pie.get_graph_obj().render_notebook())

    put_html(user.wordcloud.get_graph_obj().render_notebook())

    put_markdown("---")

    user_slug_from_cookie: Optional[str] = get_user_slug_cookies()
    if not user_slug_from_cookie:  # 没有 Cookie 信息，新用户
        put_markdown(
            f"""
            您正在查看 {user.name} 的年度统计数据。
            """
        )
        put_button(
            "生成自己的统计数据",
            onclick=lambda: jump_to(get_jump_link("join_queue")),
            color="secondary",
            block=True,
            outline=True,
        )
    elif user_slug_from_cookie != user.slug:  # 有 Cookie 信息，但查看的不是自己的数据
        put_markdown(
            f"""
            您正在查看 {user.name} 的年度统计数据。
            """
        )
        put_button(
            "查看自己的统计数据",
            onclick=lambda: jump_to(get_jump_link("display", {"user_slug": user.slug})),
            color="secondary",
            block=True,
            outline=True,
        )
    elif user_slug_from_cookie == user.slug:  # 查看的是自己的数据
        current_link: str = get_current_link()
        put_markdown(
            """
            您可以复制以下链接分享给其它简友，让他们查看您的统计数据：
            """
        )
        put_row(
            [
                put_input(
                    "share_link",
                    type="text",
                    value=current_link,
                    readonly=True,
                ),
                None,
                put_button(
                    "复制",
                    onclick=lambda: on_copy_link_button_clicked(current_link),
                    color="secondary",
                    outline=True,
                ),
            ],
            size="auto 10px 60px",
        )
