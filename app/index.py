from pywebio.output import put_markdown
from utils.config import config


def index():
    """落格
    """
    put_markdown(
        f"""
        # 落格

        版本：{config.version}
        """
    )
