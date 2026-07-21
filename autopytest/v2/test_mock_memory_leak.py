#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
内存泄漏专项 Mock 测试

覆盖：
- Engine 实例 GC
- Result 对象批量创建后 GC
- fetch 获取的大数据对象 GC
- 连接泄漏检测（Pool 的 acquire/release 计数匹配）

全部使用 Mock，无需真实 MySQL 数据库。
"""

import gc
import warnings
import weakref
from unittest.mock import AsyncMock, patch

from pymysql.err import MySQLError

from asmysql.v2 import Engine
from autopytest.v2.conftest import make_mock_conn, make_mock_pool, make_result

# ── TestEngineMemoryLeak：Engine 实例 GC ───────────────────────────────


class TestEngineMemoryLeak:
    """Engine 实例的垃圾回收"""

    def test_engine_gc_after_disconnect(self):
        """Engine 实例可被 GC（disconnect 后）"""
        engine = Engine(host="127.0.0.1", port=3306)
        ref = weakref.ref(engine)
        del engine
        gc.collect()
        assert ref() is None

    def test_engine_no_lru_cache_leak(self):
        """repr/str 不阻止 GC（无 lru_cache 强引用）"""
        engine = Engine(host="127.0.0.1", port=3306)
        ref = weakref.ref(engine)
        _ = repr(engine)
        _ = str(engine)
        del engine
        gc.collect()
        assert ref() is None

    async def test_engine_gc_after_connect_disconnect(self):
        """connect + disconnect 后 Engine 可被 GC"""
        pool = make_mock_pool()
        with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=pool)):
            engine = Engine(host="127.0.0.1", port=3306)
            ref = weakref.ref(engine)
            await engine.connect()
            await engine.disconnect()
            del engine
            gc.collect()
            assert ref() is None


# ── TestResultMemoryLeak：Result 对象 GC ───────────────────────────────


class TestResultMemoryLeak:
    """Result 对象的垃圾回收"""

    async def test_result_gc_after_close(self):
        """Result close() 后可被 GC"""
        conn, cursor = make_mock_conn()
        pool = make_mock_pool(conn)
        result = make_result(pool=pool)
        ref = weakref.ref(result)
        async with result:
            pass
        del result
        gc.collect()
        assert ref() is None

    def test_multiple_results_gc(self):
        """批量 Result 创建后全部 GC"""
        pool = make_mock_pool()
        refs = []
        for i in range(20):
            r = make_result(pool=pool, query=f"SELECT {i}")
            refs.append(weakref.ref(r))
        del r
        gc.collect()
        leaked = sum(1 for ref in refs if ref() is not None)
        assert leaked == 0, f"{leaked} Result instances leaked"

    def test_result_del_warns_unclosed(self):
        """未关闭的 Result 在 GC 时发出 ResourceWarning"""
        conn, cursor = make_mock_conn()
        pool = make_mock_pool(conn)
        result = make_result(pool=pool)
        # 模拟已执行但未关闭
        result._Result__cursor = cursor
        result._Result__executed = True
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result.__del__()
            resource_warnings = [x for x in w if issubclass(x.category, ResourceWarning)]
            assert len(resource_warnings) >= 1


# ── TestDataMemoryLeak：fetch 数据 GC ──────────────────────────────────


class TestDataMemoryLeak:
    """fetch 获取的数据对象 GC"""

    async def test_large_fetch_all_gc(self):
        """fetch_all 大数据后，数据可被 GC"""
        conn, cursor = make_mock_conn()
        # 模拟大量数据
        large_data = [(i, f"name_{i}", f"email_{i}@example.com") for i in range(1000)]
        cursor.fetchall = AsyncMock(return_value=large_data)
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)

        result = make_result(pool=pool)
        async with result as r:
            data = await r.fetch_all()
            assert len(data) == 1000

        # 删除数据引用后 GC 不崩溃
        del data
        del r
        gc.collect()
        # 验证无异常即可（list 不支持 weakref）

    async def test_cursor_reference_cleared(self):
        """close() 后 cursor 引用为 None"""
        conn, cursor = make_mock_conn()
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        result = make_result(pool=pool)
        async with result:
            pass
        # 通过 name-mangled 属性检查 cursor 已被清除
        assert result._Result__cursor is None


# ── TestConnectionLeak：连接泄漏检测 ───────────────────────────────────


class TestConnectionLeak:
    """连接泄漏检测：acquire/release 计数匹配"""

    async def test_acquire_release_parity(self):
        """正常路径 acquire/release 计数匹配"""
        conn, cursor = make_mock_conn()
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        result = make_result(pool=pool)
        async with result:
            pass
        # pool.acquire 调用 1 次，pool.release 调用 1 次
        pool.acquire.assert_awaited_once()
        pool.release.assert_called_once_with(conn)

    async def test_error_path_releases_connection(self):
        """异常路径释放连接"""
        conn, cursor = make_mock_conn()
        cursor.execute = AsyncMock(side_effect=MySQLError(1064, "Syntax error"))
        pool = make_mock_pool(conn)
        result = make_result(pool=pool)
        async with result as r:
            assert r.error is not None
        pool.release.assert_called_with(conn)

    async def test_ddl_auto_release(self):
        """DDL 语句自动释放连接"""
        conn, cursor = make_mock_conn()
        cursor.description = None
        cursor.rowcount = 0
        pool = make_mock_pool(conn)
        result = make_result(pool=pool, query="CREATE TABLE t (id INT)")
        await result.__call__()
        pool.release.assert_called_with(conn)

    async def test_fetch_all_releases(self):
        """fetch_all 后释放连接"""
        conn, cursor = make_mock_conn()
        cursor.fetchall = AsyncMock(return_value=[(1,), (2,)])
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        result = make_result(pool=pool)
        async with result as r:
            await r.fetch_all()
        pool.release.assert_called_with(conn)

    async def test_iterate_releases(self):
        """iterate() 完整迭代后释放连接"""
        conn, cursor = make_mock_conn()
        items = [(1,), (2,)]
        idx = 0

        async def mock_fetchone():
            nonlocal idx
            if idx < len(items):
                item = items[idx]
                idx += 1
                return item
            return None

        cursor.fetchone = mock_fetchone
        pool = make_mock_pool(conn)
        result = make_result(pool=pool)
        async with result as r:
            async for _ in r.iterate():
                pass
        pool.release.assert_called_with(conn)

    async def test_async_for_break_releases(self):
        """async for break 后通过 aclose() 释放连接"""
        conn, cursor = make_mock_conn()
        items = [(1,), (2,), (3,)]
        idx = 0

        async def mock_fetchone():
            nonlocal idx
            if idx < len(items):
                item = items[idx]
                idx += 1
                return item
            return None

        cursor.fetchone = mock_fetchone
        pool = make_mock_pool(conn)
        result = make_result(pool=pool)
        it = result.__aiter__()
        try:
            async for _ in it:
                break
        finally:
            await it.aclose()
        pool.release.assert_called_with(conn)

    async def test_multiple_operations_no_leak(self):
        """多次操作后无连接泄漏"""
        conn, cursor = make_mock_conn()
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)

        for _ in range(10):
            result = make_result(pool=pool)
            async with result:
                pass

        # acquire/release 应各调用 10 次
        assert pool.acquire.await_count == 10
        assert pool.release.call_count == 10
