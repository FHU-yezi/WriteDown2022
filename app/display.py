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
    is_full_width,
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
        # 该页面必须使用 user_slug 才能展示
        toast_error_and_return("请求参数错误")

    # 尝试使用 user_slug 从数据库中获取对应记录
    try:
        user = User.from_slug(user_slug_from_query_arg)
    except ValueError:
        toast_error_and_return("请求参数错误")

    # 如果数据未获取完成，也未出现异常，提示数据获取中
    if not user.is_analyze_done and not user.is_error:
        put_markdown(
            f"""
            我们正在全力获取您的数据，过一会再来试试吧。

            当前有 {get_waiting_users_count()} 人正在排队。
            """
        )
        return
    # 如果发生异常，展示错误信息
    elif user.is_error:
        put_markdown(
            f"""
            很抱歉，在{"获取数据" if user.is_fetch_error else "分析数据"}的过程中发生了异常。

            错误信息：{user.error_info}
            """
        )
        return

    user.result_shown()

    # 一切正常，展示统计数据

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

    # 如果图表不能完整展示，提示左右滑动查看
    if not is_full_width():
        put_markdown(grey_text("（左右滑动查看图表）"))

    put_html(user.heat_graph.get_graph().render_notebook())

    put_html(user.interaction_type.get_graph().render_notebook())

    put_html(user.interaction_per_hour.get_graph().render_notebook())

    put_html(user.wordcloud.get_graph().render_notebook())

    put_markdown("---")

    # 分享链接部分

    user_slug_from_cookie: Optional[str] = get_user_slug_cookies()

    # 没有 Cookie 信息，新用户
    # 提示生成自己的统计数据
    if not user_slug_from_cookie:
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

    # 有 Cookie 信息，但查看的不是自己的数据
    # 提示查看自己的统计数据
    elif user_slug_from_cookie != user.slug:
        put_markdown(
            f"""
            您正在查看 {user.name} 的年度统计数据。
            """
        )
        put_button(
            "查看自己的统计数据",
            onclick=lambda: jump_to(
                get_jump_link(
                    "display",
                    {"user_slug": user_slug_from_cookie},
                )
            ),
            color="secondary",
            block=True,
            outline=True,
        )

    # 查看的是自己的数据
    # 提示将数据分享给其他简友
    elif user_slug_from_cookie == user.slug:
        current_link: str = get_current_link()
        put_markdown("分享链接：")
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
