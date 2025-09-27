from functools import lru_cache
from typing import final

from ._engine import Engine


class AsMysql:
    """Mysql编写业务逻辑的类"""

    @final
    def __init__(self, engine: Engine):
        self.__engine: Engine = engine

    @lru_cache
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.__engine.url}>"

    @lru_cache
    def __str__(self):
        return f"{self.__class__.__name__}={self.__engine.url}"

    @final
    @property
    def client(self):
        return self.__engine
