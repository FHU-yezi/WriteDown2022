from collections import Counter
from typing import Generator, Sequence, Set

from jieba import load_userdict
from jieba import logging as jieba_logging
from jieba.posseg import cut

ALLOWED_WORD_TYPES: Set[str] = {
    x.strip()
    for x in open("word_split_assets/allowed_word_types", encoding="utf-8").readlines()
}
STOPWORDS: Set[str] = {
    x.strip()
    for x in open("word_split_assets/stopwords.txt", encoding="utf-8").readlines()
}

jieba_logging.disable()
load_userdict("word_split_assets/hotwords.txt")


def get_word_freq(text_list: Sequence[str]) -> Counter:
    result: Counter = Counter()

    for text in text_list:
        word_list: Generator = (
            x.word
            for x in cut(text)
            if len(x.word) > 1
            and x.flag in ALLOWED_WORD_TYPES
            and x.word not in STOPWORDS
        )
        result.update(Counter(word_list))

    return result
