from functools import lru_cache
from typing import Final, Generic, Iterator, Optional, Sequence, TypeVar, Union

from pymysql.cursors import Cursor, DictCursor, SSCursor, SSDictCursor
from pymysql.err import MySQLError

from ._sync_pool import Pool

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

    def close(self):
        conn = self.__cursor.connection
        self.__cursor.close()
        if conn:
            self.pool.release(conn)

    def __enter__(self):
        self.__conn_autoclose = False
        self.__call__()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.error:
            return
        self.close()

    def __iter__(self):
        """支持 for item in result 语法"""
        self.__conn_autoclose = False
        self.__call__()
        return self

    def __next__(self) -> T:
        """支持 for item in result 语法"""
        if self.error:
            # 有错误则不迭代
            raise StopIteration
        else:
            # noinspection PyUnresolvedReferences
            data = self.fetch_one()
            if data is not None:
                return data
            else:
                self.close()
                raise StopIteration

    def __call__(self):
        """
        实际执行sql查询的内部方法
        """
        # 重用 Engine 中的 execute 逻辑
        if self.__executed:
            return self
        cursor_class = _get_cursor_class(result_class=self._result_class, stream=self.stream)
        try:
            # 从连接池获取连接
            conn = self.pool.acquire()
            self.__cursor = conn.cursor(cursor_class)
            if self.__execute_many:
                self.__cursor.executemany(self.query, self.values)
            else:
                self.__cursor.execute(self.query, self.values)
            if self.commit:
                self.__cursor.connection.commit()
        except MySQLError as err:
            self.__cursor.close()
            self.pool.release(self.__cursor.connection)
            self.__error = err
        finally:
            self.__executed = True
        return self

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
        if self.error:
            return None
        return self.__cursor.lastrowid

    @property
    def row_number(self):
        """（这个属性实际就是当前已获取到的总行数）
        获取当前游标的位置:
        用于返回当前游标在结果集中的行索引（从0开始），若无法确定索引则返回 None
        """
        if self.error:
            return None
        return self.__cursor.rownumber

    def fetch_one(self, close: bool = None) -> Optional[T]:
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
        data: tuple | dict = self.__cursor.fetchone()
        if data is None:
            self.close()
            return None
        if self._result_class is not tuple and self._result_class is not dict:
            _data: T = self._result_class(**data)
        else:
            _data: T = data
        if self.__conn_autoclose:
            self.close()
        return _data

    def fetch_many(self, size: int = None, close: bool = None) -> list[T]:
        """获取多条记录"""
        if close is None:
            close = self.__conn_autoclose

        _data: list[T] = []
        if self.error or not self.__cursor:
            return _data
        # noinspection PyUnresolvedReferences
        data = self.__cursor.fetchmany(size)
        if not data:
            self.close()
            return _data
        if self._result_class is not tuple and self._result_class is not dict:
            _data = [self._result_class(**item) for item in data]
        else:
            _data = data
        if self.__conn_autoclose:
            self.close()
        return _data

    def fetch_all(self) -> list[T]:
        """获取所有记录"""
        _data: list[T] = []
        if self.error or not self.__cursor:
            return _data
        # noinspection PyUnresolvedReferences
        data = self.__cursor.fetchall()
        if self._result_class is not tuple and self._result_class is not dict:
            _data: list[T] = [self._result_class(**item) for item in data]
            return _data
        else:
            _data: list[T] = data
        self.close()
        return _data

    def iterate(self) -> Iterator[T]:
        """生成器遍历所有记录"""
        if self.error or not self.__cursor:
            # 有错误则不迭代
            return
            # 直接return等价于以下代码:
            # raise StopIteration
        else:
            try:
                while True:
                    # noinspection PyUnresolvedReferences
                    data = self.__cursor.fetchone()
                    if data:
                        if self._result_class is not tuple and self._result_class is not dict:
                            _data: T = self._result_class(**data)
                        else:
                            _data: T = data
                        yield _data
                    else:
                        break
            finally:
                self.close()
