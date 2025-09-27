from functools import lru_cache
from typing import (
    AsyncContextManager,
    AsyncIterator,
    Awaitable,
    Final,
    Optional,
    Sequence,
    TypedDict,
    TypeVar,
    Union,
    final,
    overload,
)
from urllib import parse

from aiomysql import Pool, create_pool
from pymysql.err import MySQLError

from ._error import err_msg
from ._result import Result

# 定义类型变量
T = TypeVar("T")


class EngineStatus(TypedDict):
    address: str
    connected: bool
    pool_minsize: Optional[int]
    pool_maxsize: Optional[int]
    pool_size: Optional[int]
    pool_free: Optional[int]
    pool_used: Optional[int]


class Engine:
    # noinspection SpellCheckingInspection
    """异步的数据库aiomysql封装类"""

    host: str = "127.0.0.1"
    port: int = 3306
    user: str = ""
    password: str = ""
    charset: str = "utf8mb4"
    min_pool_size: int = 1
    max_pool_size: int = 10
    pool_recycle: float = -1  # 空闲TCP连接回收等待时间（秒）
    connect_timeout: int = 5  # 连接超时时间（秒）
    auto_commit: bool = True
    echo_sql_log: bool = False  # 是否打印sql语句日志
    # result_dict: bool = False  # 返回结果是否为字典
    stream: bool = False  # 是否使用流式返回结果
    result_class: type = tuple  # 返回结果类型

    @final
    def __init__(
        self,
        url: str = None,
        *,
        host: str = None,
        port: int = None,
        user: str = None,
        password: str = None,
        charset: str = None,
        min_pool_size: int = None,
        max_pool_size: int = None,
        pool_recycle: float = None,
        connect_timeout: int = None,
        auto_commit: bool = None,
        echo_sql_log: bool = None,
        # result_dict: bool = None,
        stream: bool = None,
        result_class: type = None,
    ):
        """
        url: mysql://user:password@host:port/?charset=utf8mb4
        """
        if url:
            parsed = parse.urlparse(url)
            if parsed.scheme != "mysql":
                raise ValueError(f"Invalid url scheme: {parsed.scheme}") from None
            query_params = parse.parse_qs(parsed.query)
            host = parsed.hostname or host
            port = parsed.port or port
            user = parsed.username or user
            password = parsed.password or password
            charset = query_params.get("charset", [charset])[0]
            # 修复参数解析逻辑，避免None值传递给int()函数
            min_pool_size_val = query_params.get("min_pool_size", [min_pool_size])[0]
            min_pool_size = int(min_pool_size_val) if min_pool_size_val is not None else min_pool_size
            max_pool_size_val = query_params.get("max_pool_size", [max_pool_size])[0]
            max_pool_size = int(max_pool_size_val) if max_pool_size_val is not None else max_pool_size
            pool_recycle_val = query_params.get("pool_recycle", [pool_recycle])[0]
            pool_recycle = float(pool_recycle_val) if pool_recycle_val is not None else pool_recycle
            connect_timeout_val = query_params.get("connect_timeout", [connect_timeout])[0]
            connect_timeout = int(connect_timeout_val) if connect_timeout_val is not None else connect_timeout
            auto_commit = True if query_params.get("auto_commit", [None])[0] else auto_commit
            echo_sql_log = True if query_params.get("echo_sql_log", [None])[0] else echo_sql_log

        self.host: Final[str] = host or self.host
        self.port: Final[int] = port or self.port
        self.user: Final[str] = user or self.user
        self.password: Final[str] = password or self.password
        self.charset: Final[str] = charset or self.charset
        self.min_pool_size: Final[int] = min_pool_size or self.min_pool_size
        self.max_pool_size: Final[int] = max_pool_size if max_pool_size is not None else self.max_pool_size
        self.pool_recycle: Final[float] = pool_recycle or self.pool_recycle
        self.connect_timeout: Final[int] = connect_timeout or self.connect_timeout
        self.auto_commit: Final[bool] = auto_commit if auto_commit is not None else self.auto_commit
        self.echo_sql_log: Final[bool] = echo_sql_log if echo_sql_log is not None else self.echo_sql_log
        # self.result_dict: Final[bool] = result_dict if result_dict is not None else self.result_dict
        self.stream: Final[bool] = stream if stream is not None else self.stream
        self.result_class: Final[type] = result_class if result_class is not None else self.result_class

        self.url: Final[str] = f"mysql://{self.host}:{self.port}/"
        self.__pool: Optional[Pool] = None

    @lru_cache
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.url}>"

    @lru_cache
    def __str__(self):
        return f"{self.__class__.__name__}={self.url}"

    def __aenter__(self):
        return self.connect()

    def __aexit__(self, exc_type, exc_value, exc_tb):
        return self.disconnect()

    @final
    async def connect(self):
        """连接到mysql,建立TCP链接，初始化连接池。"""
        if not self.__pool:
            try:
                # noinspection PyUnresolvedReferences
                self.__pool = await create_pool(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    minsize=self.min_pool_size,
                    maxsize=self.max_pool_size,
                    pool_recycle=self.pool_recycle,
                    connect_timeout=self.connect_timeout,
                    autocommit=self.auto_commit,
                    echo=self.echo_sql_log,
                )
            except MySQLError as err:
                raise ConnectionError(err_msg(err)) from None
        return self

    @final
    @property
    def status(self):
        """返回数据库连接池状态"""
        _status: EngineStatus = {
            "address": self.url,
            "connected": True if self.is_connected else False,
            "pool_minsize": self.__pool.minsize if self.__pool else None,
            "pool_maxsize": self.__pool.maxsize if self.__pool else None,
            "pool_size": self.__pool.size if self.__pool else None,
            "pool_free": self.__pool.freesize if self.__pool else None,
            "pool_used": self.__pool.size - self.__pool.freesize if self.__pool else None,
        }
        return _status

    @final
    def __await__(self):
        return self.connect().__await__()

    @final
    async def __call__(self):
        return await self.connect()

    @final
    async def disconnect(self):
        """等待所有连接释放，并正常关闭mysql连接"""
        if self.__pool and not self.__pool.closed:
            self.__pool.close()
            await self.__pool.wait_closed()
            self.__pool = None

    @final
    async def release_connections(self):
        """释放连接池中所有空闲的连接"""
        await self.__pool.clear()

    @final
    @property
    def is_connected(self):
        """数据库是否已连接"""
        return True if self.__pool else False

    @final
    @property
    def pool(self):
        if not self.__pool:
            raise ConnectionError(
                f"Please connect to mysql first, function use in instance:  await {self.__class__.__name__}.connect()"
            ) from None
        return self.__pool

    @overload
    def execute(
        self,
        query: str,
        values: Union[Sequence, dict] = None,
        *,
        stream: bool = None,
        result_class: type[tuple] = tuple,
        commit: bool = None,
    ) -> Union[Awaitable[Result[tuple]], AsyncContextManager[Result[tuple]], AsyncIterator[tuple]]:
        """
        Execute a SQL statement and return a Result object
        支持两种用法:
        1. result = await execute(...)
        2. async with execute(...) as result:

        :param query: SQL statement
        :param values: parameters, can be a tuple or dictionary
        :param stream: whether to stream the result
        :param result_class: the class tuple to use for the result
        :param commit: whether to commit the transaction, default is auto
        """
        ...

    @overload
    def execute(
        self,
        query: str,
        values: Union[Sequence, dict] = None,
        *,
        stream: bool = None,
        result_class: type[T],
        commit: bool = None,
    ) -> Union[Awaitable[Result[T]], AsyncContextManager[Result[T]], AsyncIterator[T]]:
        """
        Execute a SQL statement and return a Result object
        支持两种用法:
        1. result = await execute(...)
        2. async with execute(...) as result:

        :param query: SQL statement
        :param values: parameters, can be a tuple or dictionary
        :param stream: whether to stream the result
        :param result_class: the custom class to use for the result
        :param commit: whether to commit the transaction, default is auto
        """
        ...

    @final
    def execute(
        self,
        query: str,
        values: Union[Sequence, dict] = None,
        *,
        stream: bool = None,
        result_class: type = None,
        commit: bool = None,
    ) -> Union[Awaitable[Result], AsyncContextManager[Result], AsyncIterator]:
        """
        Execute a SQL statement and return a Result object
        支持两种用法:
        1. result = await execute(...)
        2. async with execute(...) as result:

        :param query: SQL statement
        :param values: parameters, can be a tuple or dictionary
        :param stream: whether to stream the result
        :param result_class: the class to use for the result
        :param commit: whether to commit the transaction, default is auto
        """
        _stream = stream if stream is not None else self.stream
        result_class = result_class if result_class is not None else self.result_class

        return Result(
            pool=self.__pool,
            query=query,
            values=values,
            execute_many=False,
            stream=_stream,
            commit=commit,
            result_class=result_class,
        )

    @overload
    def execute_many(
        self,
        query: str,
        values: Sequence[Union[Sequence, dict]],
        *,
        stream: bool = None,
        result_class: type[tuple] = tuple,
        commit: bool = None,
    ) -> Union[Awaitable[Result[tuple]], AsyncContextManager[Result[tuple]], AsyncIterator[tuple]]:
        """
        Execute a SQL statement and return a Result object
        支持两种用法:
        1. result = await execute_many(...)
        2. async with execute_many(...) as result:

        :param query: SQL statement
        :param values: parameters, can be a tuple or dictionary
        :param stream: whether to stream the result
        :param result_class: the class tuple to use for the result
        :param commit: whether to commit the transaction, default is auto
        """
        ...

    @overload
    def execute_many(
        self,
        query: str,
        values: Sequence[Union[Sequence, dict]],
        *,
        stream: bool = None,
        result_class: type[T],
        commit: bool = None,
    ) -> Union[Awaitable[Result[T]], AsyncContextManager[Result[T]], AsyncIterator[T]]:
        """
        Execute a SQL statement and return a Result object
        支持两种用法:
        1. result = await execute_many(...)
        2. async with execute_many(...) as result:

        :param query: SQL statement
        :param values: parameters, can be a tuple or dictionary
        :param stream: whether to stream the result
        :param result_class: the custom class to use for the result
        :param commit: whether to commit the transaction, default is auto
        """
        ...

    @final
    def execute_many(
        self,
        query: str,
        values: Sequence[Union[Sequence, dict]],
        *,
        # result_dict: bool = None,
        stream: bool = None,
        result_class: type = None,
        commit: bool = None,
    ) -> Union[Awaitable[Result], AsyncContextManager[Result], AsyncIterator]:
        """
        Execute a SQL statement and return a Result object
        支持两种用法:
        1. result = await execute_many(...)
        2. async with execute_many(...) as result:

        :param query: SQL statement
        :param values: parameters, can be a tuple or dictionary
        :param stream: whether to stream the result
        :param result_class: the class to use for the result
        :param commit: whether to commit the transaction, default is auto
        """
        _stream = stream if stream is not None else self.stream
        result_class = result_class if result_class is not None else self.result_class

        return Result(
            pool=self.__pool,
            query=query,
            values=values,
            execute_many=True,
            stream=_stream,
            commit=commit,
            result_class=result_class,
        )
