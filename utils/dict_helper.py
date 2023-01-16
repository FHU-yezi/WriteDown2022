from typing import Dict


def get_reversed_dict(item: Dict) -> Dict:
    return {v: k for k, v in item.items()}


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
