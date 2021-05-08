def repl_at(string: str, _idx: int, _new: str) -> str:
    return string[:_idx] + _new + string[_idx + 1:]


def repl_last(string: str, _old: str, _new: str):
    return repl_at(string, string.rindex(_old), _new)
