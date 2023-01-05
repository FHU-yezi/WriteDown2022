from pywebio.output import put_html, put_markdown

from data.user import User, get_waiting_users_count
from utils.page import get_query_params
from widgets.toast import toast_error_and_return

NAME: str = "数据展示"
DESC: str = "查看您的年度统计结果"
VISIBILITY: bool = False


def display() -> None:
    user_id = get_query_params().get("user")
    if not user_id:
        toast_error_and_return("请求参数错误")

    try:
        user = User.from_id(user_id)
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
            很抱歉，在获取数据的过程中出现了异常。

            错误信息：{user.error_info}
            """
        )
        return

    put_html(user.heat_graph.get_graph_obj().render_notebook())

    put_html(user.wordcloud.get_graph_obj().render_notebook())
