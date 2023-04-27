from threading import Thread
from time import sleep
from typing import List

from analyzers import ANALYZE_FUNCS
from analyzers.general_data import analyze_general_data
from data.user import UserStatus, get_waiting_user
from fetcher import fetch_timeline_data
from utils.config import config
from utils.db import user_db
from utils.log import run_logger


def queue_processor_thread(start_sleep_time: int) -> None:
    sleep(start_sleep_time)

    while True:
        user = get_waiting_user()
        if not user:
            sleep(config.queue_processor.check_interval)
            continue

        user.set_status_fetching()
        run_logger.debug("开始采集用户时间线数据", user_id=user.id)
        try:
            fetch_timeline_data(user)
        except Exception as e:
            user.set_status_fetch_error("获取时间线数据失败")
            run_logger.error("获取用户时间线数据时发生异常", user_id=user.id, exception=e)
            continue
        else:
            user.set_status_waiting_for_analyze()
            run_logger.debug("用户时间线数据采集完成", user_id=user.id)

        user.set_status_analyzing()
        for analyze_item_name, analyze_func in ANALYZE_FUNCS.items():
            try:
                analyze_func(user)
            except Exception as e:
                user.set_status_analyze_error(f"分析{analyze_item_name}失败")
                run_logger.error("分析数据时发生异常", user_id=user.id, analyze_item_name=analyze_item_name, exception=e)
                break
            else:
                user.set_status_analyze_done()
                run_logger.debug("数据分析成功", user_id=user.id, analyze_item_name=analyze_item_name)

        run_logger.debug("已完成该用户的全部处理流程", user_id=user.id)


def general_data_analyzer_thread() -> None:
    while True:
        sleep(config.general_analyzer.analyze_interval)
        try:
            analyze_general_data()
        except Exception as e:
            run_logger.error("分析整体总结数据时发生异常", exception=e)
        else:
            run_logger.debug("已成功分析整体总结数据")


def clean_unfinished_job() -> None:
    cleaned_count = user_db.update_many(
        {
            "status": UserStatus.FETCHING,
        },
        {
            "$set": {
                "status": UserStatus.WAITING_FOR_FETCH,
            }
        },
    ).modified_count
    if cleaned_count:
        run_logger.warning("有未完成的任务，已重新加入队列", unfinished_task_count=cleaned_count)
    else:
        run_logger.info("没有未完成的任务")


def start_queue_processor_threads() -> List[Thread]:
    threads_list: List[Thread] = []

    run_logger.debug(f"将启动 {config.queue_processor.threads} 个队列处理线程")
    for i in range(config.queue_processor.threads):

        thread = Thread(
            target=queue_processor_thread,
            name=f"queue-processor-{i}",
            daemon=True,
            kwargs={
                "start_sleep_time": config.queue_processor.check_interval
                / config.queue_processor.threads
                * (i + 1)
            },
        )
        thread.start()
        threads_list.append(thread)

    thread = Thread(
        target=general_data_analyzer_thread,
        name="general_data_analyzer",
        daemon=True,
    )
    thread.start()
    threads_list.append(thread)

    return threads_list
