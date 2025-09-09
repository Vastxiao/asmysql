from typing import Final, Optional
from typing import AsyncIterator
from functools import lru_cache
from aiomysql import Cursor
from pymysql.err import MySQLError


class Result:
    def __init__(self, query: str, *, rows: int = None,
                 cursor: Cursor = None, error: MySQLError = None):
        if bool(cursor) ^ bool(error):
            self.query: Final[str] = query
            self.rows: Final[int] = rows
            self.cursor: Final[Cursor] = cursor
            self.error: Final[MySQLError] = error
        else:
            raise AttributeError("require arg: cursor or err") from None

    @lru_cache
    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.query}>'

    @property
    @lru_cache
    def error_no(self):
        return self.error.args[0] if self.error else 0

    @property
    @lru_cache
    def error_msg(self):
        return self.error_msg[1] if self.error_msg else ""

    @property
    def row_count(self):
        """获取受影响的行数"""
        return self.cursor.rowcount if not self.error else None

    @property
    def last_rowid(self):
        """获取最近插入的记录的ID"""
        return self.cursor.lastrowid if not self.error else None

    @property
    def row_number(self):
        """获取当前游标的位置:
        用于返回当前游标在结果集中的行索引（从0开始），若无法确定索引则返回 None
        """
        return self.cursor.rownumber if not self.error else None

    async def fetch_one(self) -> Optional[tuple]:
        """获取一条记录"""
        if not self.error:
            # noinspection PyUnresolvedReferences
            return await self.cursor.fetchone()
        return None

    async def fetch_many(self, size: int = None) -> list[tuple]:
        """获取多条记录"""
        if not self.error:
            # noinspection PyUnresolvedReferences
            return await self.cursor.fetchmany(size)
        return []

    async def fetch_all(self) -> list[tuple]:
        """获取所有记录"""
        if not self.error:
            # noinspection PyUnresolvedReferences
            return await self.cursor.fetchall()
        return []

    async def iterate(self) -> AsyncIterator[tuple]:
        """异步生成器遍历所有记录"""
        if not self.error:
            while True:
                # noinspection PyUnresolvedReferences
                data = await self.cursor.fetchone()
                if data:
                    yield data
                else:
                    break
