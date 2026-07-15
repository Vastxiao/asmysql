import warnings
import weakref
from typing import Final, Generic, Optional, Sequence, TypeVar, Union, cast

from aiomysql import Connection, Cursor, DictCursor, Pool, SSCursor, SSDictCursor
from pymysql.err import MySQLError

from ._error import err_msg

T = TypeVar("T")

# 每个 Pool 对应的已初始化连接集合（WeakSet），用于避免对同一连接重复执行 init_sql。
# 使用 WeakKeyDictionary 以 Pool 对象为 key，当 Pool 被 GC 时条目自动清理。
_initialized_conns: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()


def _get_cursor_class(*, result_class, stream: bool):
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
        values: Union[Sequence, dict, None] = None,
        execute_many: bool = False,
        stream: Optional[bool] = None,
        commit: Optional[bool] = None,
        result_class: type[T] = tuple,
        init_sql: Optional[str] = None,
    ):
        self.pool: Final[Pool] = pool
        self.query: Final[str] = query
        self.values: Final[Union[Sequence, dict, None]] = values
        self.__execute_many: Final[bool] = execute_many
        self.stream: Final[bool] = stream if stream is not None else False
        self.commit: Final[bool] = commit if commit is not None else True
        self._result_class: Final[type[T]] = result_class
        self.__init_sql: Final[Optional[str]] = init_sql
        self.__cursor: Optional[Cursor] = None
        self.__executed: bool = False
        self.__error: Optional[MySQLError] = None
        self.__conn_autoclose: bool = True
        # 缓存 rowcount / lastrowid，以便在游标关闭后仍可访问
        self.__rowcount: Optional[int] = None
        self.__lastrowid: Optional[int] = None

    # @property
    # def cursor(self):
    #     return self.__cursor

    @property
    def error(self):
        return self.__error

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.query}>"

    def __del__(self):
        """GC 时的安全网。"""
        try:
            if self.__cursor:
                warnings.warn(
                    f"{self.__class__.__name__} 未被正确关闭（应使用 async with / async for / close()）。"
                    f"连接未归还连接池以避免污染。 SQL: {self.query!r}",
                    ResourceWarning,
                    stacklevel=1,
                    source=self,
                )
        except Exception:
            pass

    async def close(self):
        """关闭游标并释放连接回连接池。可安全重复调用。"""
        cursor, self.__cursor = self.__cursor, None
        if cursor is None:
            return
        conn = cursor.connection
        try:
            await cursor.close()
        except Exception:
            pass
        finally:
            if conn and self.pool:
                self.pool.release(conn)

    async def __aenter__(self):
        self.__conn_autoclose = False
        await self.__call__()
        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        await self.close()

    async def __aiter__(self):
        """支持 async for item in result 语法。

        使用 async generator + try/finally 确保即使 break 也能正确释放连接。
        """
        self.__conn_autoclose = False
        try:
            await self.__call__()
            if self.error:
                return
            while True:
                data = await self.fetch_one(close=False)
                if data is not None:
                    yield data
                else:
                    break
        finally:
            await self.close()

    async def __anext__(self):
        """保留以兼容直接调用 __anext__ 的场景。推荐使用 async for 或 iterate()。"""
        await self.__call__()
        """支持 async for item in result 语法"""
        if self.error:
            # 有错误则不迭代
            raise StopAsyncIteration
        else:
            # noinspection PyUnresolvedReferences
            data = await self.fetch_one(close=False)
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
        conn: Connection | None = None
        try:
            # noinspection PyUnresolvedReferences
            conn = cast(Connection, await self.pool.acquire())
            self.__cursor = cast(Cursor, await conn.cursor(cursor_class))
            # 连接级初始化：每条新 TCP 连接首次使用时自动执行 init_sql
            if self.__init_sql:
                initialized = _initialized_conns.get(self.pool)
                if initialized is None:
                    initialized = weakref.WeakSet()
                    _initialized_conns[self.pool] = initialized
                if conn not in initialized:
                    await self.__cursor.execute(self.__init_sql)
                    await self.__cursor.connection.commit()  # type: ignore
                    initialized.add(conn)
            if self.__execute_many:
                await self.__cursor.executemany(self.query, self.values)
            else:
                await self.__cursor.execute(self.query, self.values)
            # 对于 stream 模式，不自动提交（steam下commit后流会获取不到数据）
            if self.commit and not self.stream:
                await self.__cursor.connection.commit()  # type: ignore
            # 非流式模式下，如果语句不返回结果集（DDL/INSERT/UPDATE 等），
            # 自动关闭游标并释放连接回连接池，避免连接泄漏。
            # cursor.description 为 None 表示该语句无结果集可供获取。
            if not self.stream and self.__cursor.description is None:
                # 缓存 rowcount / lastrowid，以便游标关闭后仍可访问
                self.__rowcount = self.__cursor.rowcount
                self.__lastrowid = self.__cursor.lastrowid
                conn_to_release = conn
                await self.__cursor.close()
                self.__cursor = None
                self.pool.release(conn_to_release)
                conn = None  # 防止 except 块重复释放
        except Exception as err:
            if self.__cursor is not None:
                try:
                    await self.__cursor.close()
                except Exception:
                    pass
                self.__cursor = None
            if conn is not None:
                self.pool.release(conn)
            if isinstance(err, MySQLError):
                self.__error = err
            else:
                raise
        finally:
            self.__executed = True
        return self

    def __await__(self):
        """
        支持 result = await execute(...) 用法
        """
        return self.__call__().__await__()

    def error_no(self):
        """获取错误码

        没有错误的话返回0
        """
        __err_no: int = self.error.args[0] if self.error else 0
        return __err_no

    def error_msg(self):
        """获取错误信息

        如果没有错误则返回空字符串
        """
        __err_msg: str = err_msg(self.error) if self.error else ""
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
        # 游标已关闭时使用缓存值（DDL/DML 语句执行后会自动释放连接）
        if self.__cursor is None:
            return self.__rowcount
        return self.__cursor.rowcount

    @property
    def last_rowid(self):
        """
        获取最近插入的记录的ID

        这个属性就是用于获取insert数据的最新插入ID
        如果没插入insert数据，则返回None
        如果mysql报错，则返回None
        """
        if self.error:
            return None
        # 游标已关闭时使用缓存值（DDL/DML 语句执行后会自动释放连接）
        if self.__cursor is None:
            return self.__lastrowid
        return self.__cursor.lastrowid

    @property
    def row_number(self):
        """（这个属性实际就是当前已获取到的总行数）
        获取当前游标的位置:
        用于返回当前游标在结果集中的行索引（从0开始），若无法确定索引则返回 None
        """
        if self.error or self.__cursor is None:
            return None
        return self.__cursor.rownumber

    async def fetch_one(self, close: Optional[bool] = None):
        """获取一条记录

        :param close: 是否自动关闭游标连接
                      注意：如果设置不关闭游标连接，必须自己调用 Result.close() 释放连接(否则连接池可能有问题)。
        :return: 返回一条记录，如果没有数据则返回None
        """
        if close is not None:
            self.__conn_autoclose = close
        if self.error or self.__cursor is None:
            return None
        # noinspection PyUnresolvedReferences
        data = await self.__cursor.fetchone()
        if data is None:
            if self.__conn_autoclose:
                await self.close()
            return None
        if self._result_class is not tuple and self._result_class is not dict:
            _data: T = self._result_class(**data)
        else:
            _data: T = data
        if self.__conn_autoclose:
            await self.close()
        return _data

    async def fetch_many(self, size: Optional[int] = None, close: Optional[bool] = None):
        """获取多条记录

        :param size: 获取记录的数量
        :param close: 是否自动关闭游标连接
                      注意：如果设置不关闭游标连接，必须自己调用 Result.close() 释放连接(否则连接池可能有问题)。
        """
        if close is not None:
            self.__conn_autoclose = close

        _data: list[T] = []
        if self.error or self.__cursor is None:
            return _data
        # noinspection PyUnresolvedReferences
        data: list = await self.__cursor.fetchmany(size)
        if not data:
            if self.__conn_autoclose:
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
        if self.error or self.__cursor is None:
            return _data
        # noinspection PyUnresolvedReferences
        data: list = await self.__cursor.fetchall()
        if self._result_class is not tuple and self._result_class is not dict:
            _data: list[T] = [self._result_class(**item) for item in data]
        else:
            _data: list[T] = data
        await self.close()
        return _data

    async def iterate(self):
        """异步生成器遍历所有记录"""
        if self.error or self.__cursor is None:
            # 有错误则不迭代
            return
            # 直接return等价于以下代码:
            # raise StopAsyncIteration
        else:
            try:
                while True:
                    # noinspection PyUnresolvedReferences
                    data = await self.__cursor.fetchone()
                    if data is not None:
                        if self._result_class is not tuple and self._result_class is not dict:
                            _data: T = self._result_class(**data)
                        else:
                            _data: T = data
                        yield _data
                    else:
                        break
            finally:
                await self.close()
