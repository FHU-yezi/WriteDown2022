from typing import Callable, List

from pywebio import start_server
from pywebio.output import put_markdown

from queue_processor import clean_unfinished_job, start_queue_processor_threads
from utils.config import config
from utils.log import run_logger
from utils.module_finder import Module, get_all_modules_info
from utils.page import get_jump_link
from utils.patch import patch_all
from widgets.card import put_app_card

NAME: str = "落格"
DESC: str = ""
VISIBILITY: bool = False

modules_list = get_all_modules_info(config.base_path)
run_logger.debug(f"模块数量：{len(modules_list)}")


def index():
    """落格"""
    put_markdown(
        f"""
        # 落格

        版本：{config.version}
        """
    )

    config.refresh()

    for module in modules_list:
        if not module.page_visibility:
            continue

        put_app_card(
            name=module.page_name,
            url=get_jump_link(module.page_func_name),
            desc=module.page_desc,
        )

    put_app_card(
        name="反馈表单",
        url="https://wenjuan.feishu.cn/m?t=sP3KbOMtblJi-76re",
        desc="",
    )


modules_list.append(
    Module(
        page_func_name="index",
        page_func=index,
        page_name="落格",
        page_desc="",
        page_visibility=False,
    )
)

func_list: List[Callable[[], None]] = [
    patch_all(module).page_func for module in modules_list
]
run_logger.debug("视图函数代码注入已完成")

clean_unfinished_job()
run_logger.debug("已清理未完成的任务")

start_queue_processor_threads()
run_logger.debug("队列处理线程已启动")

run_logger.debug("正在启动网页服务")
run_logger.info("服务启动")
start_server(
    func_list,
    host="0.0.0.0",
    port=config.deploy.port,
    debug=config.deploy.debug,
    cdn=config.deploy.PyWebIO_CDN if config.deploy.enable_PyWebIO_CDN else False,
)
