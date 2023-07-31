from typing import Final, Optional
from typing import AsyncIterator
from functools import lru_cache
from aiomysql import Cursor


class Result:
    def __init__(self, query: str, *, rows: int = None, cursor: Cursor = None, err: Exception = None):
        if bool(cursor) ^ bool(err):
            self.query: Final[str] = query
            self.rows: Final[int] = rows
            self.__cursor: Final[Cursor] = cursor
            self.err: Final[Exception] = err
        else:
            raise AttributeError("require arg: cursor or err")

    @lru_cache
    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.query}>'

    @property
    @lru_cache
    def err_msg(self):
        if self.err:
            err_str = self.err.__str__() or self.err.__doc__.replace('\n', '')
            return f"{self.err.__class__.__name__} {err_str}"
        else:
            return ""

    async def fetch_one(self) -> Optional[tuple]:
        """获取一条记录"""
        if not self.err:
            return await self.__cursor.fetchone()

    async def fetch_many(self, size: int = None) -> list[tuple]:
        """获取多条记录"""
        if not self.err:
            return await self.__cursor.fetchmany(size)

    async def fetch_all(self) -> list[tuple]:
        """获取所有记录"""
        if not self.err:
            return await self.__cursor.fetchall()

    async def iterate(self) -> AsyncIterator[tuple]:
        """异步生成器遍历所有记录"""
        if not self.err:
            while True:
                data = await self.fetch_one()
                if data:
                    yield data
                else:
                    break
