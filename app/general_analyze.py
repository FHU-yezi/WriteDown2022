from pywebio.output import put_html, put_markdown, put_warning

from data.general_analyze import GeneralData
from utils.html import grey_text, link

NAME: str = "聚合分析"
DESC: str = "查看「落格」用户的综合数据"
VISIBILITY: bool = True


def general_analyze() -> None:
    put_markdown("# 聚合分析")

    try:
        data = GeneralData.get_latest()
    except ValueError:
        put_warning("聚合分析数据暂不可用，请稍后再试")
        return

    put_markdown(grey_text(f"分析时间：{data.analyze_time.replace(microsecond=0)}"))

    put_markdown(
        f"""
        参与人数：{data.total_users_count}

        互动数据量：{data.total_interactions_count}
        """
    )

    put_markdown("## 热门用户")

    put_markdown(
        "- "
        + "\n- ".join(
            [
                (
                    f"{link(x['name'], x['jianshu_url'], new_window=True)}："
                    f"被访问 {x['view_count']} 次"
                    f"（{link('点击跳转', x['report_url'], new_window=True)}）"
                )
                for x in data.popular_users_data
            ]
        ),
        sanitize=False,
    )

    put_html(data.get_active_graph().render_notebook())
