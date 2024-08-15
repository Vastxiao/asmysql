
def err_msg(err: Exception):
    """处理报错消息，避免exception为空字符导致日志打印内容为空"""
    err_str = err.__str__() or f'{err.__doc__!r}'
    err_str = err_str.lstrip().rstrip()
    return f"{err.__class__} {err_str}"
