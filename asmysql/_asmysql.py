from functools import lru_cache
from typing import Final, final, Optional
from aiomysql import Pool, create_pool

from .__cursor_client import CursorClient


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

    @final
    def __init__(self, host: str = None, port: int = None,
                 user: str = None, password: str = None,
                 database: str = None, charset: str = None,
                 min_pool_size: int = None, max_pool_size: int = None,
                 pool_recycle: float = None, connect_timeout: int = None):
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

        self.url: Final[str] = f'mysql://{self.host}:{self.port}{"/" + self.database if self.database else ""}'
        self.__pool: Optional[Pool] = None
        self.__cursor_client: Optional[CursorClient] = None

    @lru_cache
    def __repr__(self):
        return f'<{self.__class__.__name__} {self.url}>'

    @final
    async def connect(self):
        """连接到mysql,建立TCP链接，初始化连接池。"""
        if not self.__pool:
            self.__pool = await create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                db=self.database,
                minsize=self.min_pool_size,
                maxsize=self.max_pool_size,
                echo=f'{self.url}',
                pool_recycle=self.pool_recycle,
                connect_timeout=self.connect_timeout,
            )
            self.__cursor_client = CursorClient(self.__pool)
        return self

    @final
    async def disconnect(self):
        """等待所有连接释放，并正常关闭mysql连接"""
        if not self.__pool.closed:
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
        if self.__pool:
            return True
        else:
            return False

    @final
    @property
    def pool(self):
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
