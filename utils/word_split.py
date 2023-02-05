from collections import Counter
from typing import Dict, Generator, Iterable, Set

from jieba import load_userdict
from jieba import logging as jieba_logging
from jieba.posseg import cut

ALLOWED_WORD_TYPES: Set[str] = {
    x.strip()
    for x in open(  # noqa
        "word_split_assets/allowed_word_types.txt", encoding="utf-8"
    ).readlines()
}

jieba_logging.disable()
load_userdict("word_split_assets/hotwords.txt")


def get_word_freq(text_list: Iterable[str]) -> Counter:
    result: Counter = Counter()

    for text in text_list:
        word_list: Generator = (
            x.word
            for x in cut(text)
            if len(x.word) > 1
            and x.flag in ALLOWED_WORD_TYPES
        )
        result.update(Counter(word_list))

    return result


def word_split_postprocess(data: Dict[str, int]) -> Dict[str, int]:
    # 该函数假设传入的 data 字典是按照值倒序排列的
    if len(data) <= 1000:
        return data

    return dict(tuple(data.items())[:1000])
