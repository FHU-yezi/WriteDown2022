from threading import Thread
from time import sleep
from typing import List

from analyzer import analyze_active_heat_graph, analyze_comment_word_freq
from data.user import get_waiting_user
from fetcher import fetch_timeline_data
from utils.config import config
from utils.log import run_logger


def queue_processor_thread() -> None:
    while True:
        user = get_waiting_user()
        if not user:
            sleep(config.queue_processor.check_interval)
            run_logger.debug(f"队列为空，{config.queue_processor.check_interval} 秒后再次查询")
            continue

        fetch_timeline_data(user)
        analyze_active_heat_graph(user)
        analyze_comment_word_freq(user)


def start_queue_processor_threads() -> List[Thread]:
    threads_list: List[Thread] = []

    run_logger.debug(f"将启动 {config.queue_processor.threads} 个队列处理线程")
    for i in range(config.queue_processor.threads):
        thread = Thread(
            target=queue_processor_thread,
            name=f"queue-processor-{i}",
            daemon=True,
        )
        thread.start()
        threads_list.append(thread)

    return threads_list
