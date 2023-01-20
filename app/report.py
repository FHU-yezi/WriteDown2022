from typing import Optional

from pywebio.output import Output, put_html, put_markdown, put_row
from pywebio.pin import put_input

from data.user import User, get_waiting_users_count
from utils.constants import GRAPH_REPORT_ITEM_NAME, TEXT_REPORT_ITEM_NAME
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
    remove_user_slug_cookies,
)
from widgets.button import put_button
from widgets.popup import put_error_popup, put_processing_popup
from widgets.toast import toast_error_and_return, toast_success

NAME: str = "数据展示"
DESC: str = "查看您的年度统计数据"
VISIBILITY: bool = False


def on_clear_cookie_button_clicked() -> None:
    remove_user_slug_cookies()
    toast_success("清除成功")
    jump_to(get_jump_link("join_queue"), delay=1)


def put_generate_my_report(current_report_user_name: str) -> Output:
    put_markdown(
        f"""
        您正在查看 {current_report_user_name} 的年度统计数据。
        """
    )
    put_button(
        "生成自己的统计数据",
        onclick=lambda: jump_to(get_jump_link("join_queue")),
        color="secondary",
        block=True,
        outline=True,
    )


def put_show_my_report(current_report_user_name: str, self_user_slug: str) -> Output:
    put_markdown(
        f"""
        您正在查看 {current_report_user_name} 的年度统计数据。
        """
    )
    put_button(
        "查看自己的统计数据",
        onclick=lambda: jump_to(
            get_jump_link(
                "report",
                {"user_slug": self_user_slug},
            )
        ),
        color="secondary",
        block=True,
        outline=True,
    )


def put_share_my_report() -> Output:
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


def put_text_report_item(user: User, argument_name: str, item_name: str) -> Output:
    text_data_obj = user.__getattribute__(argument_name)
    if text_data_obj.is_aviliable:
        put_markdown(
            text_data_obj.get_report(),
            sanitize=False,
        )
    else:
        put_markdown(grey_text(f"抱歉，您的数据不符合生成{item_name}的标准。"))


def put_graph_report_item(user: User, argument_name: str, item_name: str) -> Output:
    text_data_obj = user.__getattribute__(argument_name)
    if text_data_obj.is_aviliable:
        put_html(text_data_obj.get_graph().render_notebook())
    else:
        put_markdown(grey_text(f"抱歉，您的数据不符合生成{item_name}的标准。"))


def on_copy_link_button_clicked(current_link: str) -> None:
    copy_to_clipboard(current_link)
    toast_success("复制成功")


def report() -> None:
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
        put_processing_popup(
            user_name=user.name,
            waiting_users_count=get_waiting_users_count(),
            clear_cookie_callback=on_clear_cookie_button_clicked,
        )
        return

    # 如果发生异常，展示错误信息
    if user.is_error:
        put_error_popup(user.error_info)
        return

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

    for argument_name, item_name in TEXT_REPORT_ITEM_NAME.items():
        put_text_report_item(user, argument_name, item_name)

    # 如果图表不能完整展示，提示左右滑动查看
    if not is_full_width():
        put_markdown(grey_text("（左右滑动查看图表）"))

    for argument_name, item_name in GRAPH_REPORT_ITEM_NAME.items():
        put_graph_report_item(user, argument_name, item_name)

    put_markdown("---")

    # 分享链接部分

    user_slug_from_cookie: Optional[str] = get_user_slug_cookies()

    # 没有 Cookie 信息，新用户
    # 提示生成自己的统计数据
    if not user_slug_from_cookie:
        put_generate_my_report(
            current_report_user_name=user.name,
        )

    # 有 Cookie 信息，但查看的不是自己的数据
    # 提示查看自己的统计数据
    elif user_slug_from_cookie != user.slug:
        put_show_my_report(
            current_report_user_name=user.name,
            self_user_slug=user_slug_from_cookie,
        )

    # 查看的是自己的数据
    # 提示将数据分享给其他简友
    elif user_slug_from_cookie == user.slug:
        put_share_my_report()
