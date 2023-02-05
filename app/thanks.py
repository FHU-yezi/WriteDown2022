from typing import Any, Dict

from pywebio.output import put_markdown
from yaml import safe_load

from utils.html import link

NAME: str = "鸣谢"
DESC: str = "感谢这些简友 / 项目为「落格」做出的贡献"
VISIBILITY: bool = True


THANKS_DATA: Dict[str, Any] = safe_load(open("thanks.yaml", encoding="utf-8"))  # noqa


def thanks() -> None:
    put_markdown("# 鸣谢")

    put_markdown("## 内测成员")

    put_markdown(
        "- "
        + "\n- ".join(
            [
                link(name, url, new_window=True)
                for name, url in THANKS_DATA["beta_members"].items()
            ]
        ),
        sanitize=False,
    )

    put_markdown("## 开源项目")

    put_markdown(
        "- "
        + "\n- ".join(
            [
                link(name, url, new_window=True)
                for name, url in THANKS_DATA["opensource_projects"].items()
            ]
        ),
        sanitize=False,
    )
