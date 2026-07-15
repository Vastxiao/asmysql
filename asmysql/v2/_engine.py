import asyncio
from typing import (
    AsyncContextManager,
    AsyncGenerator,
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
    echo_sql_log: bool = False  # 是否打印sql语句日志
    result_class: type = tuple  # 返回结果类型
    init_sql: Optional[str] = None  # 连接初始化时自动执行的 SQL（如 SET）

    @final
    def __init__(
        self,
        url: Optional[str] = None,
        *,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        charset: Optional[str] = None,
        min_pool_size: Optional[int] = None,
        max_pool_size: Optional[int] = None,
        pool_recycle: Optional[float] = None,
        connect_timeout: Optional[int] = None,
        echo_sql_log: Optional[bool] = None,
        result_class: Optional[type] = None,
        init_sql: Optional[str] = None,
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
            user = parse.unquote(parsed.username) if parsed.username else user
            password = parse.unquote(parsed.password) if parsed.password else password
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
            echo_sql_log_val = query_params.get("echo_sql_log", [None])[0]
            if echo_sql_log_val is not None:
                echo_sql_log = echo_sql_log_val.lower() in ("true", "1", "yes")
            init_sql = query_params.get("init_sql", [init_sql])[0]

        self.host: Final[str] = host if host is not None else self.host
        self.port: Final[int] = port if port is not None else self.port
        self.user: Final[str] = user if user is not None else self.user
        self.password: Final[str] = password if password is not None else self.password
        self.charset: Final[str] = charset if charset is not None else self.charset
        self.min_pool_size: Final[int] = min_pool_size if min_pool_size is not None else self.min_pool_size
        self.max_pool_size: Final[int] = max_pool_size if max_pool_size is not None else self.max_pool_size
        self.pool_recycle: Final[float] = pool_recycle if pool_recycle is not None else self.pool_recycle
        self.connect_timeout: Final[int] = connect_timeout if connect_timeout is not None else self.connect_timeout
        self.echo_sql_log: Final[bool] = echo_sql_log if echo_sql_log is not None else self.echo_sql_log
        self.result_class: Final[type] = result_class if result_class is not None else self.result_class
        self.init_sql: Final[Optional[str]] = init_sql if init_sql is not None else self.init_sql

        self.url: Final[str] = f"mysql://{self.user}@{self.host}:{self.port}/"
        self.__pool: Optional[Pool] = None
        # 延迟创建 asyncio.Lock，避免跨事件循环使用问题
        self._connect_lock: Optional[asyncio.Lock] = None

    def _get_connect_lock(self) -> asyncio.Lock:
        """获取连接锁，延迟创建以绑定当前事件循环。"""
        if self._connect_lock is None:
            self._connect_lock = asyncio.Lock()
        return self._connect_lock

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.url}>"

    def __str__(self):
        return f"{self.__class__.__name__}={self.url}"

    def __aenter__(self):
        return self.connect()

    def __aexit__(self, exc_type, exc_value, exc_tb):
        return self.disconnect()

    @final
    async def connect(self):
        """连接到mysql,建立TCP链接，初始化连接池。"""
        async with self._get_connect_lock():
            if not self.__pool:
                try:
                    # noinspection PyUnresolvedReferences
                    self.__pool = await create_pool(
                        host=self.host,
                        port=self.port,
                        user=self.user,
                        password=self.password,
                        charset=self.charset,
                        minsize=self.min_pool_size,
                        maxsize=self.max_pool_size,
                        pool_recycle=self.pool_recycle,  # type: ignore
                        connect_timeout=self.connect_timeout,
                        autocommit=False,
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
            "connected": self.is_connected,
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
        async with self._get_connect_lock():
            pool, self.__pool = self.__pool, None
            if pool and not pool.closed:
                pool.close()
                await pool.wait_closed()

    @final
    async def release_connections(self):
        """释放连接池中所有空闲的连接"""
        if self.__pool:
            await self.__pool.clear()

    @final
    @property
    def is_connected(self):
        """数据库是否已连接"""
        return self.__pool is not None

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
        values: Optional[Union[Sequence, dict]] = None,
        *,
        stream: Optional[bool] = None,
        result_class: type[tuple] = tuple,
        commit: Optional[bool] = None,
    ) -> Union[AsyncContextManager[Result[tuple]], AsyncGenerator[tuple, None]]: ...

    @overload
    def execute(
        self,
        query: str,
        values: Union[Sequence, dict] | None = None,
        *,
        stream: Optional[bool] = None,
        result_class: type[T],
        commit: Optional[bool] = None,
    ) -> Union[AsyncContextManager[Result[T]], AsyncGenerator[T, None]]: ...

    @final
    def execute(
        self,
        query: str,
        values: Optional[Union[Sequence, dict]] = None,
        *,
        stream: Optional[bool] = None,
        result_class: Optional[type[T]] = None,
        commit: Optional[bool] = None,
    ) -> Union[AsyncContextManager[Result[T]], AsyncGenerator[T, None]]:
        """
        Execute a SQL statement and return a Result object
        支持两种用法:
        1. async with execute(...) as result:
        2. async for item in execute(...):

        :param query: SQL statement
        :param values: parameters, can be a tuple or dictionary
        :param stream: whether to stream the result
        :param result_class: the class to use for the result
        :param commit: whether to commit the transaction, default is auto
        """
        _result_class: type = self.result_class
        if result_class is not None:
            _result_class = result_class

        return Result[T](
            pool=self.pool,
            query=query,
            values=values,
            execute_many=False,
            stream=stream,
            commit=commit,
            result_class=_result_class,
            init_sql=self.init_sql,
        )

    @overload
    def execute_many(
        self,
        query: str,
        values: Sequence[Union[Sequence, dict]],
        *,
        stream: Optional[bool] = None,
        result_class: type[tuple] = tuple,
        commit: Optional[bool] = None,
    ) -> Union[AsyncContextManager[Result[tuple]], AsyncGenerator[tuple, None]]: ...

    @overload
    def execute_many(
        self,
        query: str,
        values: Sequence[Union[Sequence, dict]],
        *,
        stream: Optional[bool] = None,
        result_class: type[T],
        commit: Optional[bool] = None,
    ) -> Union[AsyncContextManager[Result[T]], AsyncGenerator[T, None]]: ...

    @final
    def execute_many(
        self,
        query: str,
        values: Sequence[Union[Sequence, dict]],
        *,
        stream: Optional[bool] = None,
        result_class: Optional[type[T]] = None,
        commit: Optional[bool] = None,
    ) -> Union[AsyncContextManager[Result[T]], AsyncGenerator[T, None]]:
        """
        Execute a SQL statement and return a Result object
        支持两种用法:
        1. async with execute_many(...) as result:
        2. async for item in execute_many(...):

        :param query: SQL statement
        :param values: parameters, can be a tuple or dictionary
        :param stream: whether to stream the result
        :param result_class: the class to use for the result
        :param commit: whether to commit the transaction, default is auto
        """
        result_class = result_class if result_class is not None else self.result_class

        return Result[T](
            pool=self.pool,
            query=query,
            values=values,
            execute_many=True,
            stream=stream,
            commit=commit,
            result_class=result_class,
            init_sql=self.init_sql,
        )
