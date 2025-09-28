from collections import deque
from threading import Condition, Lock
from typing import Deque, Final, Set

import pymysql
from dbutils.pooled_db import PooledDB
from pymysql.connections import Connection


class Pool:
    """
    基于 DBUtils 实现的同步 MySQL 连接池，功能仿照 aiomysql.Pool
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
        if min_pool_size < 0:
            raise ValueError("minsize should be zero or greater")
        if max_pool_size < min_pool_size and max_pool_size != 0:
            raise ValueError("maxsize should be not less than minsize")

        self._minsize = min_pool_size
        self._conn_kwargs = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "charset": charset,
            "connect_timeout": connect_timeout,
            **kwargs,
        }

        # 连接池相关属性
        self._free: Deque[Connection] = deque(maxlen=max_pool_size or None)
        self._used: Set[Connection] = set()
        self._terminated: Set[Connection] = set()
        self._acquiring = 0
        self._closing = False
        self._closed = False
        self._echo = echo_sql_log
        self._recycle = pool_recycle

        # 线程同步相关
        self._lock = Lock()
        self._cond = Condition(self._lock)

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

        # 填充初始连接池
        if min_pool_size > 0:
            with self._cond:
                self._fill_free_pool(False)

    @property
    def echo(self):
        return self._echo

    @property
    def minsize(self):
        return self._minsize

    @property
    def maxsize(self):
        return self._free.maxlen

    @property
    def size(self):
        return self.freesize + len(self._used) + self._acquiring

    @property
    def freesize(self):
        return len(self._free)

    def clear(self):
        """Close all free connections in pool."""
        with self._cond:
            while self._free:
                conn = self._free.popleft()
                conn.close()
            self._cond.notify()

    @property
    def closed(self):
        """
        The readonly property that returns ``True`` if connections is closed.
        """
        return self._closed

    def close(self):
        """Close pool.

        Mark all pool connections to be closed on getting back to pool.
        Closed pool doesn't allow to acquire new connections.
        """
        if self._closed:
            return
        self._closing = True

    def terminate(self):
        """Terminate pool.

        Close pool with instantly closing all acquired connections also.
        """
        self.close()

        for conn in list(self._used):
            conn.close()
            self._terminated.add(conn)

        self._used.clear()

    def wait_closed(self):
        """Wait for closing all pool's connections."""
        if self._closed:
            return
        if not self._closing:
            raise RuntimeError(".wait_closed() should be called after .close()")

        while self._free:
            conn = self._free.popleft()
            conn.close()

        with self._cond:
            while self.size > self.freesize:
                self._cond.wait()

        self._closed = True

    def acquire(self):
        """Acquire free connection from the pool."""
        return self._acquire()

    def _acquire(self):
        if self._closing:
            raise RuntimeError("Cannot acquire connection after closing pool")
        with self._cond:
            while True:
                self._fill_free_pool(True)
                if self._free:
                    conn = self._free.popleft()
                    assert not conn.closed, conn
                    assert conn not in self._used, (conn, self._used)
                    self._used.add(conn)
                    return conn
                else:
                    self._cond.wait()

    def _fill_free_pool(self, override_min):
        # iterate over free connections and remove timed out ones
        free_size = len(self._free)
        n = 0
        while n < free_size:
            conn = self._free[-1]

            # 检查连接是否已经关闭
            if conn._sock is None:
                self._free.pop()
                conn.close()
            # 检查连接是否超时
            elif self._recycle > -1:
                # 在DBUtils中，连接超时由maxusage参数控制，这里简化处理
                self._free.rotate()
            else:
                self._free.rotate()
            n += 1

        while self.size < self.minsize:
            self._acquiring += 1
            try:
                conn = self.__pool.connection()
                # raise exception if pool is closing
                self._free.append(conn)
                self._cond.notify()
            finally:
                self._acquiring -= 1
        if self._free:
            return

        if override_min and (not self.maxsize or self.size < self.maxsize):
            self._acquiring += 1
            try:
                conn = self.__pool.connection()
                # raise exception if pool is closing
                self._free.append(conn)
                self._cond.notify()
            finally:
                self._acquiring -= 1

    def _wakeup(self):
        with self._cond:
            self._cond.notify()

    def release(self, conn: Connection):
        """Release free connection back to the connection pool."""
        if conn in self._terminated:
            assert conn.closed, conn
            self._terminated.remove(conn)
            return
        assert conn in self._used, (conn, self._used)
        self._used.remove(conn)
        if not conn.closed:
            # 检查是否有活动的事务
            try:
                in_trans = conn.get_transaction_status()
                if in_trans:
                    conn.close()
                    return
            except AttributeError:
                # pymysql.Connection 可能没有 get_transaction_status 方法
                pass

            if self._closing:
                conn.close()
            else:
                self._free.append(conn)
        self._wakeup()

    @property
    def pool(self):
        """
        获取连接池对象

        :return: 连接池对象
        """
        return self.__pool

    @property
    def status(self):
        """
        获取连接池状态信息

        :return: 包含连接池状态信息的字典
        """
        return {
            "pool_minsize": self._minsize,
            "pool_maxsize": self.maxsize,
            "pool_size": len(self._free) + len(self._used) + self._acquiring,
            "pool_free": len(self._free),
            "pool_used": len(self._used),
        }
