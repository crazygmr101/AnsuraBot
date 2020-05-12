from typing import List, Dict


def descend(obj: Dict, keys: List[str]):
    temp = obj
    for k in keys:
        temp = temp[k]
    return temp
