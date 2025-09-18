from typing import Final, Optional, Union
from typing import AsyncIterator
from typing import TypeVar
from functools import lru_cache
from aiomysql import Cursor
from aiomysql import Pool
from pymysql.err import MySQLError


T = TypeVar('T')


class Result:
    def __init__(self, query: str,
                 *,
                 # rows: int = None,
                 cursor: Cursor = None,
                 pool: Pool = None,
                 result_dict: bool = False,
                 result_model: Optional[T] = None,
                 stream: bool = False,
                 error: MySQLError = None):
        if not (bool(cursor) ^ bool(error)):
            raise AttributeError("require arg: cursor or err") from None
            
        # cursor和pool必须同时提供或同时不提供（除了error情况）
        if bool(cursor) != bool(pool):
            raise AttributeError("require arg: cursor and pool") from None
            
        self.query: Final[str] = query
        # self.rows: Final[int] = rows  # rows实际就是row_count，所以这个属性没有用
        self.result_dict: Final[bool] = result_dict
        self.result_model: Final[Optional[T]] = result_model
        self.stream: Final[bool] = stream
        self.cursor: Final[Cursor] = cursor
        self.pool: Final[Pool] = pool

        self.error: Final[MySQLError] = error

    @lru_cache
    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.query}>'

    def __del__(self):
        if self.error:
            return
        conn = self.cursor.connection
        if conn:
            self.pool.release(conn)

    async def close(self):
        conn = self.cursor.connection
        await self.cursor.close()
        if conn:
            self.pool.release(conn)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        if self.error:
            return
        await self.close()

    # async def __call__(self):
    #     return self
    #
    # def __await__(self):
    #     return self

    @property
    @lru_cache
    def error_no(self):
        """获取错误码

        没有错误的话返回0
        """
        __err_no: int = self.error.args[0] if self.error else 0
        return __err_no

    @property
    @lru_cache
    def error_msg(self):
        """获取错误信息

        如果没有错误则返回空字符串
        """
        __err_msg: str = self.error_msg[1] if self.error else ""
        return __err_msg

    @property
    def row_count(self):
        """获取受影响的行数

        这个属性实际就是sql结果的总条数
        如果mysql报错，则返回None
        如果使用stream执行sql语句，则返回None
        """
        if self.error:
            return None
        if self.stream:
            return None
        return self.cursor.rowcount

    @property
    def last_rowid(self):
        """
        获取最近插入的记录的ID

        这个属性就是用于获取insert数据的最新插入ID
        如果没插入insert数据，则返回None
        如果mysql报错，则返回None
        """
        return self.cursor.lastrowid if not self.error else None

    @property
    def row_number(self):
        """（这个属性实际就是当前已获取到的总行数）
        获取当前游标的位置:
        用于返回当前游标在结果集中的行索引（从0开始），若无法确定索引则返回 None
        """
        return self.cursor.rownumber if not self.error else None

    async def fetch_one(self, close: bool = True) -> Optional[Union[tuple,  dict,  T]]:
        """获取一条记录

        :param close: 是否自动关闭游标连接
                      注意：如果设置不关闭游标连接，必须自己调用 Result.close() 释放连接(否则连接池可能有问题)。
        :return: 返回一条记录，如果没有数据则返回None
        """
        if self.error:
            return None
        # noinspection PyUnresolvedReferences
        data = await self.cursor.fetchone()
        if data is None:
            await self.close()
            return None
        if self.result_dict and self.result_model:
            return self.result_model(**data)
        if close:
            await self.close()
        return data

    async def fetch_many(self, size: int = None) -> list[Union[tuple,  dict,  T]]:
        """获取多条记录"""
        if self.error:
            return []
        # noinspection PyUnresolvedReferences
        data: list = await self.cursor.fetchmany(size)
        if data:
            if self.result_dict and self.result_model:
                data = [self.result_model(**item) for item in data]
        else:
            await self.close()
        return data

    async def fetch_all(self) -> list[Union[tuple,  dict,  T]]:
        """获取所有记录"""
        if self.error:
            return []
        # noinspection PyUnresolvedReferences
        data: list = await self.cursor.fetchall()
        if self.result_dict and self.result_model:
            return [self.result_model(**item) for item in data]
        await self.close()
        return data

    async def iterate(self) -> AsyncIterator[Union[tuple,  dict,  T]]:
        """异步生成器遍历所有记录"""
        if self.error:
            # 有错误则不迭代
            return
            # 直接return等价于以下代码:
            # raise StopAsyncIteration
        else:
            try:
                while True:
                    # noinspection PyUnresolvedReferences
                    data = await self.cursor.fetchone()
                    if data:
                        if self.result_dict and self.result_model:
                            data = self.result_model(**data)
                        yield data
                    else:
                        break
            finally:
                await self.close()
