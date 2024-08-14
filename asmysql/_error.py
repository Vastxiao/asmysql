
def err_msg(err: Exception):
    """处理报错消息，避免exception为空字符导致日志打印内容为空"""
    err_str = err.__str__() or err.__doc__.replace('\n', '\t').replace("\r", "")
    err_str = err_str.lstrip().rstrip()
    err_str = f"{err_str!r}".lstrip("'").rstrip("'")
    return f"{err.__class__.__name__} {err_str}"
