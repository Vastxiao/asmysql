from typing import Final

import pymysql
from dbutils.pooled_db import PooledDB


class Pool:
    """
    基于 DBUtils 实现的同步 MySQL 连接池
    """

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        charset: str,
        min_pool_size: int = 1,
        max_pool_size: int = 10,
        pool_recycle: float = -1,
        connect_timeout: int = 5,
        auto_commit: bool = True,
        echo_sql_log: bool = False,
        **kwargs,
    ):
        """
        初始化连接池

        :param host: 数据库主机地址
        :param port: 数据库端口
        :param user: 用户名
        :param password: 密码
        :param charset: 字符集
        :param min_pool_size: 连接池中空闲连接的最小数量
        :param max_pool_size: 连接池中允许的最大连接数
        :param pool_recycle: 空闲TCP连接回收等待时间（秒），-1表示不回收
        :param connect_timeout: 连接超时时间（秒）
        :param auto_commit: 是否自动提交事务
        :param echo_sql_log: 是否打印SQL语句日志
        :param kwargs: 其他传递给连接的参数
        """
        # 将aiomysql风格的参数转换为DBUtils参数
        mincached = min_pool_size
        maxcached = max_pool_size
        maxconnections = max_pool_size
        maxusage = None if pool_recycle < 0 else int(pool_recycle)
        blocking = True

        # 设置会话命令
        setsession = []
        if auto_commit:
            setsession.append("SET AUTOCOMMIT=1")
        else:
            setsession.append("SET AUTOCOMMIT=0")

        if echo_sql_log:
            # 注意：DBUtils没有直接支持SQL日志记录，这只是一个占位符
            pass

        self.__pool: Final[PooledDB] = PooledDB(
            creator=pymysql,
            host=host,
            port=port,
            user=user,
            password=password,
            charset=charset,
            mincached=mincached,
            maxcached=maxcached,
            maxshared=0,  # DBUtils中的共享连接特性，默认禁用
            maxconnections=maxconnections,
            blocking=blocking,
            maxusage=maxusage,
            setsession=setsession or None,
            ping=1,  # 默认检查连接有效性
            connect_timeout=connect_timeout,
            **kwargs,
        )

        # 保存配置参数，以便在status方法中使用
        self._mincached = mincached
        self._maxcached = maxcached

    @property
    def pool(self):
        """
        获取连接池对象

        :return: 连接池对象
        """
        return self.__pool

    def get_connection(self) -> pymysql.Connection:
        """
        从连接池中获取一个连接

        :return: 数据库连接对象
        """
        return self.__pool.connection()

    # def get_cursor(self, result_class):
    #     conn = self.__pool.connection()
    #     cur = conn.cursor()
    #     return cur

    def release(self, conn: pymysql.Connection):
        """
        将连接返回到连接池

        :param conn: 要释放的数据库连接
        """
        # DBUtils会自动处理连接的回收，不需要手动释放
        _ = conn

    @property
    def status(self):
        """
        获取连接池状态信息

        :return: 包含连接池状态信息的字典
        """
        return {
            "pool_minsize": self._mincached,
            "pool_maxsize": self._maxcached,
            "pool_size": len(self.__pool._idle_cache) + self.__pool._connections if self.__pool else None,
            "pool_free": len(self.__pool._idle_cache) if hasattr(self.__pool, "_idle_cache") else None,
            "pool_used": self.__pool._connections if self.__pool else None,
        }
