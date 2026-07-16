#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
asmysql v2 缺陷修复 Mock 测试

为所有已修复的 bug 编写回归测试，确保不再复现。
全部使用 Mock，无需真实 MySQL 数据库。

覆盖范围：
  P0 - 严重：连接泄漏、重复释放、异常安全
  P1 - 高：  URL 参数解析、falsy 值、并发连接、自定义异常
  P2 - 中：  执行前检查、null 安全、属性安全、迭代器边界
"""

import asyncio
import gc
import weakref
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from pydantic import BaseModel
from pymysql.err import MySQLError, OperationalError

from asmysql.v2 import Engine, Result
from asmysql.v2._error import err_msg

# ── 辅助工具 ────────────────────────────────────────────────────────


class CustomModel(BaseModel):
    """用于测试自定义 result_class 的模型"""
    id: int
    name: str


def _make_mock_cursor():
    """创建模拟的 aiomysql Cursor，包含所有常用异步方法"""
    cursor = MagicMock()
    cursor.execute = AsyncMock()
    cursor.executemany = AsyncMock()
    cursor.fetchall = AsyncMock(return_value=[])
    cursor.fetchone = AsyncMock(return_value=None)
    cursor.fetchmany = AsyncMock(return_value=[])
    cursor.close = AsyncMock()
    cursor.rowcount = 0
    cursor.lastrowid = None
    cursor.rownumber = None
    return cursor


def _make_mock_conn(cursor=None):
    """创建模拟的 aiomysql Connection，绑定 cursor"""
    conn = MagicMock()
    if cursor is None:
        cursor = _make_mock_cursor()
    cursor.connection = conn
    conn.cursor = AsyncMock(return_value=cursor)
    conn.commit = AsyncMock()
    conn.rollback = AsyncMock()
    return conn, cursor


def _make_mock_pool(conn=None):
    """创建模拟的 aiomysql Pool，带 acquire/release/close 等方法"""
    pool = MagicMock()
    pool.closed = False
    pool.acquire = AsyncMock(return_value=conn) if conn else AsyncMock()
    pool.release = Mock()
    pool.close = Mock()
    pool.wait_closed = AsyncMock()
    pool.clear = AsyncMock()
    pool.minsize = 1
    pool.maxsize = 10
    pool.size = 1
    pool.freesize = 1
    return pool


def _make_result(**kwargs):
    """创建 Result 实例，提供合理的默认 mock 值"""
    defaults = dict(
        pool=_make_mock_pool(),
        query="SELECT 1",
        values=None,
        execute_many=False,
        stream=False,
        result_class=tuple,
    )
    defaults.update(kwargs)
    return Result(**defaults)


# ═══════════════════════════════════════════════════════════════════
# P0 - Critical：连接泄漏与异常安全
# ═══════════════════════════════════════════════════════════════════


class TestP0Critical:
    """严重缺陷：连接泄漏、重复释放、异常处理"""

    async def test_fetch_all_custom_result_class_releases_connection(self):
        """Test 1: fetch_all() 使用自定义 result_class 后必须释放连接

        Bug: 当 result_class 为自定义类时，fetch_all() 提前返回而未调用 close()，
             导致连接泄漏。
        Fix: 统一在 if/else 之后调用 close()，确保所有路径都释放连接。
        """
        conn, cursor = _make_mock_conn()
        cursor.fetchall = AsyncMock(return_value=[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}])
        pool = _make_mock_pool(conn)

        result = _make_result(pool=pool, result_class=CustomModel)

        async with result as r:
            models = await r.fetch_all()

            assert len(models) == 2
            assert isinstance(models[0], CustomModel)
            assert models[0].name == "Alice"
            assert models[1].id == 2
        # 核心断言：连接必须被释放
        pool.release.assert_called_once_with(conn)

    async def test_double_release_after_mysql_error(self):
        """Test 2: SQL 执行失败后，close() 不能重复释放连接

        Bug: __call__() 捕获 MySQLError 后关闭 cursor 并释放连接，
             但没有将 __cursor 置 None，后续 close() 会再次释放同一连接。
        Fix: except 块中关闭 cursor 后立即 self.__cursor = None；
             close() 使用 cursor, self.__cursor = self.__cursor, None 原子交换。
        """
        conn, cursor = _make_mock_conn()
        cursor.execute = AsyncMock(side_effect=MySQLError(1064, "SQL syntax error"))
        pool = _make_mock_pool(conn)

        result = _make_result(pool=pool)

        async with result as r:
            pass  # SQL 失败，存储 error 并释放连接

        assert r.error is not None
        # 此时 pool.release 已调用一次
        assert pool.release.call_count == 1

        # 再次 close()：应当安全且幂等
        await r.close()
        # 核心断言：连接仅被释放一次
        assert pool.release.call_count == 1

    async def test_init_hook_releases_connection_on_init_sql_failure(self):
        """Test 3: Result.__call__ 中 init_sql 失败时必须释放连接

        Bug: cursor.execute(init_sql) 失败时，连接从未释放回连接池。
        Fix: 在 except 块中调用 pool.release(conn) 后再 raise。
        """
        conn, cursor = _make_mock_conn()
        cursor.execute = AsyncMock(side_effect=OperationalError(1064, "Invalid SQL"))
        pool = _make_mock_pool(conn)

        with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=pool)):
            engine = Engine(host="127.0.0.1", port=3306, init_sql="BAD SQL")
            await engine.connect()

        async with engine.execute("SELECT 1") as result:
            # 核心断言：错误被记录在 result 中
            assert result.error is not None
            assert result.error_no == 1064
        # 连接被释放
        pool.release.assert_called_with(conn)
        # cursor 也应被关闭
        cursor.close.assert_awaited_once()

    async def test_async_for_break_releases_connection(self):
        """Test 4: async for 中 break 后必须释放连接

        Bug: break 跳出 async for 后，__aiter__ 返回的异步生成器不再被驱动，
             __anext__ 不会被再次调用，连接永久泄漏。
        Fix: __aiter__ 改为 async generator + try/finally，确保 aclose() 能
             触发 finally 块中的 close()。

        注意：async generator 的 try/finally 中 await 操作在 GC 时可能不会执行，
        需要显式调用 aclose() 来确保清理。Python 的 async for 在 break 时应自动
        调用 aclose()，但在测试环境中显式调用更可靠。
        """
        conn, cursor = _make_mock_conn()

        items = [("row1",), ("row2",), ("row3",)]
        idx = 0

        async def mock_fetchone():
            nonlocal idx
            if idx < len(items):
                item = items[idx]
                idx += 1
                return item
            return None

        cursor.fetchone = mock_fetchone
        pool = _make_mock_pool(conn)

        result = _make_result(pool=pool)

        # 获取迭代器并显式管理生命周期
        it = result.__aiter__()
        count = 0
        try:
            async for item in it:
                count += 1
                break  # 仅取第一条后跳出
        finally:
            await it.aclose()

        assert count == 1
        # 核心断言：break 后通过 aclose() 连接仍被释放
        pool.release.assert_called_with(conn)

    async def test_non_mysql_error_releases_connection_and_reraises(self):
        """Test 5: 非 MySQLError 异常（如 OSError）必须释放连接并重新抛出

        Bug: __call__() 仅捕获 MySQLError，其他异常（OSError、
             asyncio.CancelledError 等）直接传播，但已 acquire 的连接未释放。
        Fix: 捕获 Exception，释放连接后，仅 MySQLError 存储，其余 re-raise。
        """
        conn = MagicMock()
        conn.cursor = AsyncMock(side_effect=OSError("Connection reset by peer"))
        pool = _make_mock_pool(conn)

        result = _make_result(pool=pool)

        with pytest.raises(OSError, match="Connection reset"):
            async with result:
                pass

        # 核心断言：非 MySQLError 异常也要释放连接
        pool.release.assert_called_once_with(conn)

    async def test_del_safety_pool_none(self):
        """Test 6a: pool 为 None 时 __del__ 不应抛出异常

        Bug: 旧版 __del__ 没有 try/except，pool=None 时访问 self.pool.release()
             会抛 AttributeError，导致 GC 警告甚至崩溃。
        Fix: 整个 __del__ 包裹在 try/except Exception: pass 中。
        """
        result = _make_result(pool=MagicMock())
        # 手动将 pool 置 None
        result.pool = None
        # 不应抛出
        result.__del__()

    def test_del_safety_cursor_none(self):
        """Test 6b: cursor 为 None 时 __del__ 不应抛出异常"""
        result = _make_result()
        # cursor 默认就是 None（未执行），不应抛出
        result.__del__()

    def test_del_safety_both_none(self):
        """Test 6c: pool 和 cursor 均为 None 时 __del__ 不应抛出异常"""
        result = _make_result()
        result.pool = None
        result.__del__()


# ═══════════════════════════════════════════════════════════════════
# P1 - High：参数解析与并发安全
# ═══════════════════════════════════════════════════════════════════


class TestP1High:
    """高优先级缺陷：URL 参数解析、falsy 值、并发、异常类"""

    def test_min_pool_size_zero_not_overridden(self):
        """Test 8a: min_pool_size=0 不应被默认值 1 覆盖

        Bug: 旧版用 min_pool_size or default，0 是 falsy 所以被覆盖。
        Fix: 改用 val if val is not None else default。
        """
        engine = Engine(min_pool_size=0)
        assert engine.min_pool_size == 0

    def test_pool_recycle_zero_not_overridden(self):
        """Test 8b: pool_recycle=0.0 不应被默认值覆盖"""
        engine = Engine(pool_recycle=0.0)
        assert engine.pool_recycle == 0.0

    def test_connect_timeout_zero_not_overridden(self):
        """Test 8c: connect_timeout=0 不应被默认值覆盖"""
        engine = Engine(connect_timeout=0)
        assert engine.connect_timeout == 0

    def test_falsy_zero_from_url(self):
        """Test 8d: URL 中 ?min_pool_size=0 也应正确解析为 0"""
        engine = Engine(url="mysql://u:p@host:3306/?min_pool_size=0&connect_timeout=0")
        assert engine.min_pool_size == 0
        assert engine.connect_timeout == 0

    async def test_connect_race_condition(self):
        """Test 9: 并发 connect() 只应创建一个连接池

        Bug: 多个协程同时调用 connect() 可能各自创建 pool，导致旧 pool 泄漏。
        Fix: 使用 asyncio.Lock 序列化 connect()，并在锁内二次检查 __pool。
        """
        pool = _make_mock_pool()
        create_call_count = 0

        async def mock_create_pool(**kwargs):
            nonlocal create_call_count
            create_call_count += 1
            await asyncio.sleep(0)  # 让出控制权，触发竞态
            return pool

        with patch("asmysql.v2._engine.create_pool", new=mock_create_pool):
            engine = Engine(host="127.0.0.1", port=3306)
            await asyncio.gather(
                engine.connect(),
                engine.connect(),
                engine.connect(),
            )

        # 核心断言：create_pool 仅被调用一次
        assert create_call_count == 1
        assert engine.is_connected

    async def test_write_sql_auto_commits(self):
        """写操作 SQL（INSERT/UPDATE/DELETE 等）在非 stream 模式下自动 commit

        新行为：Result 根据 SQL 语句首关键词自动判断是否需要 commit，
        无需外部传入 commit 参数。
        """
        conn, cursor = _make_mock_conn()
        pool = _make_mock_pool(conn)

        result = _make_result(pool=pool, query="INSERT INTO t VALUES (1)")
        async with result:
            pass
        conn.commit.assert_awaited_once()

    async def test_read_sql_does_not_commit(self):
        """读操作 SQL（SELECT）不自动 commit"""
        conn, cursor = _make_mock_conn()
        cursor.description = (("col",),)  # 模拟有结果集
        pool = _make_mock_pool(conn)

        result = _make_result(pool=pool, query="SELECT 1")
        async with result:
            pass
        conn.commit.assert_not_awaited()

    async def test_stream_mode_does_not_commit(self):
        """stream 模式下即使是写操作 SQL 也不 commit"""
        conn, cursor = _make_mock_conn()
        pool = _make_mock_pool(conn)

        result = _make_result(pool=pool, query="INSERT INTO t VALUES (1)", stream=True)
        async with result:
            pass
        conn.commit.assert_not_awaited()


# ═══════════════════════════════════════════════════════════════════
# P2 - Medium：边界条件与防御性编程
# ═══════════════════════════════════════════════════════════════════


class TestP2Medium:
    """中等优先级缺陷：空值检查、属性安全、迭代器边界"""

    def test_execute_before_connect_raises_clear_error(self):
        """Test 12: execute() 前未 connect() 应抛出清晰的 AsMysqlConnectionError

        Bug: execute() 将 None pool 传给 Result，导致后续 AttributeError。
        Fix: pool 属性在未连接时主动抛出 AsMysqlConnectionError 并附带提示信息。
        """
        engine = Engine(host="127.0.0.1", port=3306)
        with pytest.raises(ConnectionError) as exc_info:
            engine.execute("SELECT 1")
        assert "connect" in str(exc_info.value).lower() or "Connect" in str(exc_info.value)

    async def test_release_connections_before_connect(self):
        """Test 13a: connect() 前调用 release_connections() 不应报错

        Bug: 旧版直接调用 self.__pool.clear()，__pool 为 None 时 AttributeError。
        Fix: 添加 if self.__pool: 守卫。
        """
        engine = Engine(host="127.0.0.1", port=3306)
        # 不应抛出任何异常
        await engine.release_connections()

    async def test_release_connections_after_connect(self):
        """Test 13b: connect() 后调用 release_connections() 应清理空闲连接"""
        pool = _make_mock_pool()
        with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=pool)):
            engine = Engine(host="127.0.0.1", port=3306)
            await engine.connect()
            await engine.release_connections()

        pool.clear.assert_awaited_once()

    def test_no_lru_cache_on_repr_str(self):
        """Test 14a: __repr__/__str__ 不应使用 @lru_cache（避免强引用阻止 GC）

        Bug: @lru_cache 缓存了 self 的强引用，阻止实例被垃圾回收。
        Fix: 移除 @lru_cache，改用普通方法。
        """
        engine = Engine(host="127.0.0.1", port=3306)
        ref = weakref.ref(engine)

        # 调用 __repr__ 和 __str__
        _ = repr(engine)
        _ = str(engine)

        # 删除实例
        del engine
        gc.collect()

        # 实例应可被回收
        assert ref() is None

    def test_multiple_results_can_be_garbage_collected(self):
        """Test 14b: 多个 Result 实例应可正常 GC，无 lru_cache 残留引用"""
        pool = _make_mock_pool()
        refs = []
        for i in range(10):
            result = _make_result(pool=pool, query=f"SELECT {i}")
            refs.append(weakref.ref(result))

        del result
        gc.collect()

        leaked = sum(1 for r in refs if r() is not None)
        assert leaked == 0, f"{leaked} Result instances leaked (held by lru_cache?)"

    async def test_row_count_after_close_returns_none(self):
        """Test 15a: close() 后 row_count 应返回 None，非 AttributeError

        Bug: close() 将 __cursor 置 None 后，self.__cursor.rowcount 抛 AttributeError。
        Fix: 属性方法中先检查 self.__cursor is None，返回 None。
        """
        conn, cursor = _make_mock_conn()
        cursor.rowcount = 42
        cursor.description = (("col",),)  # 模拟有结果集
        pool = _make_mock_pool(conn)

        result = _make_result(pool=pool)
        async with result as r:
            assert r.row_count == 42

        # 核心断言：close 后不报错
        assert r.row_count is None

    async def test_last_rowid_after_close_returns_none(self):
        """Test 15b: close() 后 last_rowid 应返回 None"""
        conn, cursor = _make_mock_conn()
        cursor.lastrowid = 99
        cursor.description = (("col",),)
        pool = _make_mock_pool(conn)

        result = _make_result(pool=pool)
        async with result as r:
            assert r.last_rowid == 99

        assert r.last_rowid is None

    async def test_row_number_after_close_returns_none(self):
        """Test 15c: close() 后 row_number 应返回 None"""
        conn, cursor = _make_mock_conn()
        cursor.rownumber = 5
        cursor.description = (("col",),)
        pool = _make_mock_pool(conn)

        result = _make_result(pool=pool)
        async with result as r:
            assert r.row_number == 5

        assert r.row_number is None

    async def test_fetch_one_does_not_release_on_exhaustion(self):
        """Test 16: fetch_one() 数据耗尽时不自动释放连接

        连接生命周期由 async with 统一管理，fetch_one 本身不负责关闭连接。
        即使数据耗尽（返回 None），连接也仅在 async with 退出时释放。
        """
        conn, cursor = _make_mock_conn()
        cursor.fetchone = AsyncMock(return_value=None)
        cursor.description = (("col",),)  # 模拟有结果集
        pool = _make_mock_pool(conn)

        async with _make_result(pool=pool) as result:
            data = await result.fetch_one()
            assert data is None
            # 核心断言：连接未被释放（fetch_one 耗尽，但连接由 async with 管理）
            pool.release.assert_not_called()

    async def test_error_msg_uses_err_msg_formatter(self):
        """Test 17: error_msg 应使用 err_msg() 格式化，而非直接访问 args[1]

        Bug: 旧版用 self.error.args[1] 取值，对非标准 MySQLError 可能 IndexError。
        Fix: 改用 err_msg(self.error)，统一处理异常消息格式化。
        """
        pool = _make_mock_pool()
        error = MySQLError(1045, "Access denied for user")

        result = _make_result(pool=pool)
        # 通过 name-mangled 属性设置 error
        result._Result__error = error

        msg = result.error_msg
        expected = err_msg(error)
        assert msg == expected
        assert "MySQLError" in msg
        assert "Access denied" in msg

    async def test_error_msg_empty_when_no_error(self):
        """Test 17b: 无错误时 error_msg 应返回空字符串"""
        pool = _make_mock_pool()
        result = _make_result(pool=pool)
        assert result.error_msg == ""

    async def test_iterate_yields_empty_tuples(self):
        """Test 18: iterate() 应正确 yield 空元组

        Bug: 旧版用 if data: 判断，空元组 () 为 falsy 被跳过。
        Fix: 改用 if data is not None: 判断，空元组正常 yield。
        """
        conn, cursor = _make_mock_conn()

        items = [(1, "hello"), (), (3, "world")]
        idx = 0

        async def mock_fetchone():
            nonlocal idx
            if idx < len(items):
                item = items[idx]
                idx += 1
                return item
            return None

        cursor.fetchone = mock_fetchone
        pool = _make_mock_pool(conn)

        result = _make_result(pool=pool)
        async with result as r:
            collected = []
            async for item in r.iterate():
                collected.append(item)

        # 核心断言：空元组也应被 yield
        assert len(collected) == 3
        assert collected[0] == (1, "hello")
        assert collected[1] == ()
        assert collected[2] == (3, "world")

    async def test_aexit_always_closes_on_success(self):
        """Test 19a: async with 正常退出时 close() 必须被调用"""
        conn, cursor = _make_mock_conn()
        pool = _make_mock_pool(conn)

        result = _make_result(pool=pool)

        async with result as r:
            assert r is result

        # 核心断言
        pool.release.assert_called_with(conn)

    async def test_aexit_always_closes_on_error(self):
        """Test 19b: async with 内部抛异常时 close() 仍必须被调用

        Bug: __aexit__ 在 error 存在时跳过了 close()，导致连接泄漏。
        Fix: __aexit__ 无条件调用 await self.close()。
        """
        conn, cursor = _make_mock_conn()
        cursor.execute = AsyncMock(side_effect=MySQLError(1064, "Syntax error"))
        pool = _make_mock_pool(conn)

        result = _make_result(pool=pool)

        async with result as r:
            assert r.error is not None

        # 核心断言：即使有错误，连接也应被释放
        pool.release.assert_called_with(conn)

    async def test_close_is_idempotent(self):
        """额外: close() 可安全重复调用"""
        conn, cursor = _make_mock_conn()
        pool = _make_mock_pool(conn)

        result = _make_result(pool=pool)
        async with result:
            pass  # 执行 SQL

        assert pool.release.call_count == 1

        await result.close()
        assert pool.release.call_count == 1  # 不再增加

        await result.close()
        assert pool.release.call_count == 1  # 仍然是一次

    async def test_fetch_all_tuple_result_class(self):
        """额外: fetch_all() 使用 tuple result_class 也正常释放连接"""
        conn, cursor = _make_mock_conn()
        cursor.fetchall = AsyncMock(return_value=[(1, "a"), (2, "b")])
        pool = _make_mock_pool(conn)

        result = _make_result(pool=pool, result_class=tuple)
        async with result as r:
            rows = await r.fetch_all()
        assert len(rows) == 2
        assert rows[0] == (1, "a")
        pool.release.assert_called_with(conn)

    async def test_fetch_all_dict_result_class(self):
        """额外: fetch_all() 使用 dict result_class 也正常释放连接"""
        conn, cursor = _make_mock_conn()
        cursor.fetchall = AsyncMock(return_value=[{"id": 1}, {"id": 2}])
        pool = _make_mock_pool(conn)

        result = _make_result(pool=pool, result_class=dict)
        async with result as r:
            rows = await r.fetch_all()
        assert len(rows) == 2
        assert rows[0] == {"id": 1}
        pool.release.assert_called_with(conn)
