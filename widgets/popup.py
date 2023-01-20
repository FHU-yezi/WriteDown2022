from pywebio.output import popup, put_markdown

from utils.html import link


def put_processing_popup(user_name: str, waiting_users_count: int) -> None:
    with popup(title="数据处理中", size="large", implicit_close=False):
        put_markdown(
            f"""
            {user_name}，我们正在全力处理您的数据，过一会再来试试吧。

            当前有 {waiting_users_count} 人正在排队。
            """
        )


def put_error_popup(error_info: str) -> None:
    with popup(title="发生异常", size="large", implicit_close=False):
        # TODO
        put_markdown(
            f"""
            很抱歉，在处理您数据的过程中发生了异常。

            以下错误信息可能对解决问题有帮助：{error_info}

            请访问我们的反馈表单报告此问题：{link("点击访问", "https://wenjuan.feishu.cn/m?t=sn9OI8nublJi-tsbl", new_window=True)}
            """,
            sanitize=False,
        )
