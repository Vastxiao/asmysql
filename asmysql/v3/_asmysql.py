from functools import lru_cache
from typing import final, TypeVar, Generic
from ._sync_engine import Engine as SyncEngine
from ._async_engine import Engine as AsyncEngine

# 定义类型变量
EngineType = TypeVar('EngineType', SyncEngine, AsyncEngine)


class AsMysql(Generic[EngineType]):
    """Mysql编写业务逻辑的类"""
    @final
    def __init__(self, engine: EngineType):
        self.__engine: EngineType = engine

    @lru_cache
    def __repr__(self):
        return f'<{self.__class__.__name__} {self.__engine.url}>'

    @lru_cache
    def __str__(self):
        return f'{self.__class__.__name__}={self.__engine.url}'

    @final
    @property
    def client(self):
        return self.__engine
