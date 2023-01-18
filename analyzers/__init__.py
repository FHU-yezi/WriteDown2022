from typing import Callable, Dict

from analyzers.active_data import analyze_active_data
from analyzers.comment_word_freq import analyze_comment_word_freq
from analyzers.interaction_per_hour import analyze_interaction_per_hour
from analyzers.interaction_summary import analyze_interaction_summary_data
from analyzers.interaction_type import analyze_interaction_type
from data.user import User

ANALYZE_FUNCS: Dict[str, Callable[[User], None]] = {
    "活跃度数据": analyze_active_data,
    "评论词频数据": analyze_comment_word_freq,
    "互动类型数据": analyze_interaction_type,
    "互动小时分布数据": analyze_interaction_per_hour,
    "互动总结数据": analyze_interaction_summary_data,
}
