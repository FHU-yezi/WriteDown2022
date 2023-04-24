from functools import wraps
from typing import Any, Callable

from httpcore import NetworkError, ProtocolError
from httpx import HTTPError
from sspeedup.retry import exponential_backoff_policy, retry

from utils.log import run_logger


def retry_on_network_error(func: Callable) -> Callable:
    @retry(
        exponential_backoff_policy(),
        (HTTPError, NetworkError, ProtocolError),
        max_tries=5,
        on_retry=lambda event: run_logger.warning(
            f"发生重试，尝试次数：{event.tries}，等待时间：{event.wait}"
        ),
    )
    @wraps(func)
    def inner(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    return inner
