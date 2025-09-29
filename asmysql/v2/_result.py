from functools import lru_cache
from typing import Final, Generic, Optional, Sequence, TypeVar, Union

from aiomysql import Cursor, DictCursor, Pool, SSCursor, SSDictCursor
from pymysql.err import MySQLError

T = TypeVar("T")


def _get_cursor_class(*, result_class: T, stream: bool):
    if result_class is tuple:
        if stream:
            return SSCursor
        return Cursor
    else:
        if stream:
            return SSDictCursor
        return DictCursor


class Result(Generic[T]):
    def __init__(
        self,
        *,
        pool: Pool,
        query: str,
        values: Union[Sequence, dict] = None,
        execute_many: bool = False,
        stream: bool = False,
        commit: bool = True,
        result_class: T = tuple,
    ):
        self.pool: Final[Pool] = pool
        self.query: Final[str] = query
        self.values: Final[Union[Sequence, dict]] = values
        self.__execute_many: Final[bool] = execute_many
        self.stream: Final[bool] = stream
        self.commit: Final[bool] = commit
        self._result_class: Final[T] = result_class
        self.__cursor: Optional[Cursor] = None
        self.__executed: bool = False
        self.__error: Optional[MySQLError] = None
        self.__conn_autoclose: bool = True

    # @property
    # def cursor(self):
    #     return self.__cursor

    @property
    def error(self):
        return self.__error

    @lru_cache
    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.query}>"

    def __del__(self):
        if self.error:
            return
        if self.__cursor:
            conn = self.__cursor.connection
            if conn:
                self.pool.release(conn)

    async def close(self):
        conn = self.__cursor.connection
        await self.__cursor.close()
        if conn:
            self.pool.release(conn)

    async def __aenter__(self):
        self.__conn_autoclose = False
        await self.__call__()
        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        if self.error:
            return
        await self.close()

    def __aiter__(self):
        """支持 async for item in result 语法"""
        self.__conn_autoclose = False
        return self

    async def __anext__(self):
        await self.__call__()
        """支持 async for item in result 语法"""
        if self.error:
            # 有错误则不迭代
            raise StopAsyncIteration
        else:
            # noinspection PyUnresolvedReferences
            data = await self.fetch_one()
            if data is not None:
                return data
            else:
                await self.close()
                raise StopAsyncIteration

    async def __call__(self):
        """
        实际执行sql查询的内部方法
        """
        # 重用 Engine 中的 execute 逻辑
        if self.__executed:
            return self
        cursor_class = _get_cursor_class(result_class=self._result_class, stream=self.stream)
        try:
            # noinspection PyUnresolvedReferences
            conn = await self.pool.acquire()
            self.__cursor = await conn.cursor(cursor_class)
            if self.__execute_many:
                await self.__cursor.executemany(self.query, self.values)
            else:
                await self.__cursor.execute(self.query, self.values)
            if self.commit:
                await self.__cursor.connection.commit()
        except MySQLError as err:
            await self.__cursor.close()
            self.pool.release(self.__cursor.connection)
            self.__error = err
        finally:
            self.__executed = True
        return self

    def __await__(self):
        """
        支持 result = await execute(...) 用法
        """
        return self.__call__().__await__()

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
        __err_msg: str = self.error.args[1] if self.error else ""
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
        return self.__cursor.rowcount

    @property
    def last_rowid(self):
        """
        获取最近插入的记录的ID

        这个属性就是用于获取insert数据的最新插入ID
        如果没插入insert数据，则返回None
        如果mysql报错，则返回None
        """
        return self.__cursor.lastrowid if not self.error else None

    @property
    def row_number(self):
        """（这个属性实际就是当前已获取到的总行数）
        获取当前游标的位置:
        用于返回当前游标在结果集中的行索引（从0开始），若无法确定索引则返回 None
        """
        return self.__cursor.rownumber if not self.error else None

    async def fetch_one(self, close: bool = None):
        """获取一条记录

        :param close: 是否自动关闭游标连接
                      注意：如果设置不关闭游标连接，必须自己调用 Result.close() 释放连接(否则连接池可能有问题)。
        :return: 返回一条记录，如果没有数据则返回None
        """
        if close is not None:
            self.__conn_autoclose = close
        if self.error:
            return None
        # noinspection PyUnresolvedReferences
        data = await self.__cursor.fetchone()
        if data is None:
            await self.close()
            return None
        if self._result_class is not tuple and self._result_class is not dict:
            _data: T = self._result_class(**data)
        else:
            _data: T = data
        if self.__conn_autoclose:
            await self.close()
        return _data

    async def fetch_many(self, size: int = None, close: bool = None):
        """获取多条记录

        :param size: 获取记录的数量
        :param close: 是否自动关闭游标连接
                      注意：如果设置不关闭游标连接，必须自己调用 Result.close() 释放连接(否则连接池可能有问题)。
        """
        if close is None:
            self.__conn_autoclose = close

        _data: list[T] = []
        if self.error:
            return _data
        # noinspection PyUnresolvedReferences
        data: list = await self.__cursor.fetchmany(size)
        if not data:
            await self.close()
            return _data
        if self._result_class is not tuple and self._result_class is not dict:
            _data = [self._result_class(**item) for item in data]
        else:
            _data = data
        if self.__conn_autoclose:
            await self.close()
        return _data

    async def fetch_all(self):
        """获取所有记录"""
        _data: list[T] = []
        if self.error:
            return _data
        # noinspection PyUnresolvedReferences
        data: list = await self.__cursor.fetchall()
        if self._result_class is not tuple and self._result_class is not dict:
            _data: list[T] = [self._result_class(**item) for item in data]
            return _data
        else:
            _data: list[T] = data
        await self.close()
        return _data

    async def iterate(self):
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
                    data = await self.__cursor.fetchone()
                    if data:
                        if self._result_class is not tuple and self._result_class is not dict:
                            _data: T = self._result_class(**data)
                        else:
                            _data: T = data
                        yield _data
                    else:
                        break
            finally:
                await self.close()
