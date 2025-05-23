from functools import lru_cache
from typing import Final, final, Optional
from aiomysql import Pool, create_pool
from pymysql.err import MySQLError
from ._cursor_client import CursorClient
from ._error import err_msg


class AsMysql:
    """异步的数据库aiomysql封装类"""
    host: str = '127.0.0.1'
    port: int = 3306
    user: str = ''
    password: str = ''
    database: str = ''
    charset: str = 'utf8mb4'
    min_pool_size: int = 1
    max_pool_size: int = 10
    pool_recycle: float = -1  # 空闲TCP连接回收等待时间（秒）
    connect_timeout: int = 5  # 连接超时时间（秒）
    echo_sql_log: bool = False  # 是否打印sql语句日志

    @final
    def __init__(self, host: str = None, port: int = None,
                 user: str = None, password: str = None,
                 database: str = None, charset: str = None,
                 min_pool_size: int = None, max_pool_size: int = None,
                 pool_recycle: float = None, connect_timeout: int = None,
                 echo_sql_log: bool = None):
        self.host: Final[str] = host or self.host
        self.port: Final[int] = port or self.port
        self.user: Final[str] = user or self.user
        self.password: Final[str] = password or self.password
        self.database: Final[str] = database or self.database
        self.charset: Final[str] = charset or self.charset
        self.min_pool_size: Final[int] = min_pool_size or self.min_pool_size
        self.max_pool_size: Final[int] = max_pool_size if max_pool_size is not None else self.max_pool_size
        self.pool_recycle: Final[float] = pool_recycle or self.pool_recycle
        self.connect_timeout: Final[int] = connect_timeout or self.connect_timeout
        self.echo_sql_log: Final[bool] = echo_sql_log if echo_sql_log is not None else self.echo_sql_log

        self.url: Final[str] = f'mysql://{self.host}:{self.port}{"/" + self.database if self.database else ""}'
        self.__pool: Optional[Pool] = None
        self.__cursor_client: Optional[CursorClient] = None

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
                    echo=self.echo_sql_log,
                )
                self.__cursor_client = CursorClient(self.__pool)
            except MySQLError as err:
                raise ConnectionError(err_msg(err)) from None
        return self

    @final
    async def disconnect(self):
        """等待所有连接释放，并正常关闭mysql连接"""
        if self.__pool and not self.__pool.closed:
            self.__pool.close()
            await self.__pool.wait_closed()
            self.__pool = None
            self.__cursor_client = None

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
                                  f" await {self.__class__.__name__}.connect()")
        return self.__pool

    @final
    @property
    def client(self):
        if not self.__cursor_client:
            raise ConnectionError(f"Please connect to mysql first, function use in instance: "
                                  f" await {self.__class__.__name__}.connect()")
        return self.__cursor_client

    @final
    def __await__(self):
        return self.connect().__await__()

    @final
    async def __call__(self):
        return await self.connect()
