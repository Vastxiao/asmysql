from functools import lru_cache
from typing import Final, final, Optional
from typing import Union, Sequence
from urllib import parse
from aiomysql import Pool, create_pool
from pymysql.err import MySQLError
from ._result import Result
from ._error import err_msg


class Engine:
    # noinspection SpellCheckingInspection
    """异步的数据库aiomysql封装类"""
    host: str = '127.0.0.1'
    port: int = 3306
    user: str = ''
    password: str = ''
    charset: str = 'utf8mb4'
    min_pool_size: int = 1
    max_pool_size: int = 10
    pool_recycle: float = -1  # 空闲TCP连接回收等待时间（秒）
    connect_timeout: int = 5  # 连接超时时间（秒）
    auto_commit: bool = True
    echo_sql_log: bool = False  # 是否打印sql语句日志

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
    ):
        """
        url: mysql://user:password@host:port/?charset=utf8mb4
        """
        if url:
            parsed = parse.urlparse(url)
            if parsed.scheme != 'mysql':
                raise ValueError(f"Invalid url scheme: {parsed.scheme}") from None
            query_params = parse.parse_qs(parsed.query)
            host = parsed.hostname or host
            port = parsed.port or port
            user = parsed.username or user
            password = parsed.password or password
            charset = query_params.get('charset', [charset])[0]
            min_pool_size = int(query_params.get('min_pool_size', [min_pool_size])[0])
            max_pool_size = int(query_params.get('max_pool_size', [max_pool_size])[0])
            pool_recycle = float(query_params.get('pool_recycle', [pool_recycle])[0])
            connect_timeout = int(query_params.get('connect_timeout', [connect_timeout])[0])
            auto_commit = True if query_params.get('auto_commit', [None])[0] else auto_commit
            echo_sql_log = True if query_params.get('echo_sql_log', [None])[0] else echo_sql_log

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

        self.url: Final[str] = f'mysql://{self.host}:{self.port}/'
        self.__pool: Optional[Pool] = None

    @lru_cache
    def __repr__(self):
        return f'<{self.__class__.__name__} {self.url}>'

    @lru_cache
    def __str__(self):
        return f'{self.__class__.__name__}={self.url}'

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
                    db=self.database,
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
            raise ConnectionError(f"Please connect to mysql first, function use in instance: "
                                  f" await {self.__class__.__name__}.connect()") from None
        return self.__pool

    async def execute(self, query: str,
                      values: Union[Sequence, dict] = None,
                      *,
                      commit: bool = None,
                      ) -> Result:
        """
        Execute a SQL statement and return a Result object
        :param query: SQL statement
        :param values: parameters, can be a tuple or dictionary
        :param commit: whether to commit the transaction, default is auto
        """
        try:
            async with self.__pool.acquire() as conn:
                async with conn.cursor() as cur:
                    rows = await cur.execute(query, values)
                    if commit:
                        await conn.commit()
                    return Result(query, rows=rows, cursor=cur)
        except MySQLError as err:
            return Result(query, error=err)

    async def execute_many(self, query: str,
                           values: Sequence[Union[Sequence, dict]],
                           *,
                           commit: bool = None,
                           ) -> Result:
        """
        Execute a SQL statement and return a Result object
        :param query: SQL statement
        :param values: parameters, can be a tuple or dictionary
        :param commit: whether to commit the transaction, default is auto
        """
        try:
            async with self.__pool.acquire() as conn:
                async with conn.cursor() as cur:
                    rows = await cur.executemany(query, values)
                    if commit:
                        await conn.commit()
                    return Result(query, rows=rows, cursor=cur)
        except MySQLError as err:
            return Result(query, error=err)
