from typing import Dict, List, Tuple


def get_reversed_dict(item: Dict) -> Dict:
    result = {}
    kv_pairs: List[Tuple] = list(item.items())
    for key, value in kv_pairs:
        result[value] = key
    return result


def flatten_dict(item: Dict) -> Dict:
    result = {}
    for k, v in item.items():
        if isinstance(v, dict):  # 存在嵌套字典
            inner_item = flatten_dict(v)
            for k1, v1 in inner_item.items():
                result[f"{k}.{k1}"] = v1
        else:
            result[k] = v
    return result
