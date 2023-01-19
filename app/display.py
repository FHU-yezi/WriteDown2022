from typing import Optional

from pywebio.output import put_html, put_markdown, put_row
from pywebio.pin import put_input

from data.user import User, get_waiting_users_count
from utils.exceptions import UserNotExistError
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
from widgets.popup import show_processing_popup, show_error_popup
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
    except UserNotExistError:
        toast_error_and_return("请求参数错误")

    # 如果数据未获取完成，提示数据获取中
    if user.is_processing:
        show_processing_popup(
            user_name=user.name,
            waiting_users_count=get_waiting_users_count(),
        )
        return

    # 如果发生异常，展示错误信息
    if user.is_error:
        show_error_popup(user.error_info)

    # 触发页面浏览次数和展示时间更新
    user.result_shown()

    # 展示统计数据

    put_markdown(
        f"""
        # {user.name} 的 2022 年度数据统计

        {grey_text(
            f'生成时间：{user.end_fetch_time.strftime(r"%Y-%m-%d %H:%M:%S")} | '
            f'展示次数：{user.result_show_count}'
        )}
        """
    )

    if user.interaction_summary.is_aviliable:
        put_markdown(user.interaction_summary.get_summary(), sanitize=False,)
    else:
        put_markdown("抱歉，您的数据不符合分析互动概览的标准。")

    # 如果图表不能完整展示，提示左右滑动查看
    if not is_full_width():
        put_markdown(grey_text("（左右滑动查看图表）"))

    if user.heat_graph.is_aviliable:
        put_html(user.heat_graph.get_graph().render_notebook())
    else:
        put_markdown(grey_text("很抱歉，您的数据不符合生成互动热力图的标准。"))

    if user.interaction_type.is_aviliable:
        put_html(user.interaction_type.get_graph().render_notebook())
    else:
        put_markdown(grey_text("很抱歉，您的数据不符合生成互动类型图的标准。"))

    if user.interaction_per_hour.is_aviliable:
        put_html(user.interaction_per_hour.get_graph().render_notebook())
    else:
        put_markdown(grey_text("很抱歉，您的数据不符合生成互动小时分布图的标准。"))

    if user.wordcloud.is_aviliable:
        put_html(user.wordcloud.get_graph().render_notebook())
    else:
        put_markdown(grey_text("很抱歉，您的数据不符合生成评论词云图的标准"))

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
