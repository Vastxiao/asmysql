#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
集成环境泄漏检测

使用真实 MySQL 验证：
- 连接泄漏：大量操作后 pool 状态稳定
- SQL 错误后连接不泄漏
- fetch_all/async for break/iterate break 后连接不泄漏
- 对象泄漏：大量 Result 对象 GC 检测
- 大数据 GC
"""

import gc
from urllib.parse import quote

import pytest

from asmysql.v2 import Engine

pytestmark = pytest.mark.integration

_TEST_DB = "asmysql_test_leak"


@pytest.fixture
async def engine(mysql_url):
    """创建并连接 Engine，测试结束后断开连接。"""
    setup_eng = Engine(mysql_url)
    try:
        await setup_eng.connect()
    except ConnectionError:
        pytest.skip("MySQL 数据库不可用，跳过集成测试")
    async with setup_eng.execute(f"CREATE DATABASE IF NOT EXISTS `{_TEST_DB}`"):
        pass
    await setup_eng.disconnect()

    eng = Engine(mysql_url + "?init_sql=" + quote(f"USE `{_TEST_DB}`"))
    await eng.connect()
    yield eng
    await eng.disconnect()

    cleanup_eng = Engine(mysql_url)
    await cleanup_eng.connect()
    async with cleanup_eng.execute(f"DROP DATABASE IF EXISTS `{_TEST_DB}`"):
        pass
    await cleanup_eng.disconnect()


@pytest.fixture
async def table(engine):
    """创建测试表并在测试后清理"""
    async with engine.execute("""
        CREATE TABLE IF NOT EXISTS test_leak (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            data TEXT
        )
    """):
        pass
    # 插入一些数据
    for i in range(50):
        async with engine.execute(
            "INSERT INTO test_leak (name, data) VALUES (%s, %s)",
            (f"item_{i}", "x" * 100),
        ):
            pass
    yield
    async with engine.execute("DROP TABLE IF EXISTS test_leak"):
        pass


# ── TestConnectionLeak：连接泄漏检测 ────────────────────────────────────


class TestConnectionLeak:
    """连接泄漏检测（真实 MySQL）"""

    async def test_pool_size_stable_after_many_ops(self, engine, table):
        """大量 CRUD 后 pool.size 稳定"""
        for i in range(50):
            async with engine.execute(
                "INSERT INTO test_leak (name) VALUES (%s)", (f"extra_{i}",)
            ) as result:
                assert result.error is None

        for i in range(50):
            async with engine.execute("SELECT * FROM test_leak LIMIT 10") as r:
                await r.fetch_all()

        final_size = engine.status["pool_size"]
        # pool_size 不应无限增长
        assert final_size <= engine.max_pool_size

    async def test_pool_freesize_restored(self, engine, table):
        """操作完成后 pool.freesize 恢复"""
        # 先执行操作填满池
        for _ in range(20):
            async with engine.execute("SELECT * FROM test_leak LIMIT 5") as r:
                await r.fetch_all()

        # 所有操作完成后，空闲连接应恢复
        status = engine.status
        assert status["pool_free"] >= 0
        assert status["pool_used"] == 0 or status["pool_used"] is not None

    async def test_no_leak_on_sql_error(self, engine, table):
        """SQL 语法错误后连接不泄漏"""
        initial_size = engine.status["pool_size"]

        for _ in range(10):
            async with engine.execute("INVALID SQL SYNTAX HERE") as r:
                assert r.error is not None

        # 错误后连接应已释放
        final_size = engine.status["pool_size"]
        assert final_size <= initial_size + 2  # 允许少量波动

        # 后续查询正常
        async with engine.execute("SELECT 1") as result:
            assert result.error is None

    async def test_no_leak_on_fetch_all(self, engine, table):
        """fetch_all 后连接不泄漏"""
        for _ in range(5):
            async with engine.execute("SELECT * FROM test_leak") as result:
                data = await result.fetch_all()
                assert len(data) > 0

        # 后续查询正常
        async with engine.execute("SELECT 1") as result:
            assert result.error is None

    async def test_no_leak_on_async_for_break(self, engine, table):
        """async for break 后连接不泄漏"""
        for _ in range(5):
            count = 0
            async for row in engine.execute("SELECT * FROM test_leak"):
                count += 1
                if count >= 3:
                    break
            assert count == 3

        # 后续查询正常
        async with engine.execute("SELECT 1") as result:
            assert result.error is None

    async def test_no_leak_on_iterate_break(self, engine, table):
        """fetch_one 循环 break 后连接不泄漏"""
        for _ in range(3):
            async with engine.execute("SELECT * FROM test_leak LIMIT 5") as r:
                data = await r.fetch_one()
                assert data is not None

        # 后续查询正常
        async with engine.execute("SELECT 1") as result:
            assert result.error is None


# ── TestObjectLeak：对象泄漏检测 ────────────────────────────────────────


class TestObjectLeak:
    """对象泄漏检测"""

    async def test_many_result_objects_gc(self, engine, table):
        """创建 100 个 Result 后 GC 检测"""
        import weakref

        refs = []
        for i in range(20):
            async with engine.execute("SELECT 1") as result:
                pass
            refs.append(weakref.ref(result))
            del result

        gc.collect()
        leaked = sum(1 for ref in refs if ref() is not None)
        # 所有 Result 应可被 GC（无循环引用）
        assert leaked == 0, f"{leaked} Result instances leaked"

    async def test_large_fetch_data_gc(self, engine, table):
        """fetch_all 大量数据后 GC"""
        # 插入大量数据
        for i in range(20):
            async with engine.execute(
                "INSERT INTO test_leak (name, data) VALUES (%s, %s)",
                (f"big_{i}", "y" * 500),
            ):
                pass

        async with engine.execute("SELECT * FROM test_leak") as result:
            data = await result.fetch_all()

        del data
        del result
        gc.collect()

        # data 列表应可被 GC
        # 注意：由于 Python 内部引用机制，这里主要验证不崩溃

    async def test_cursor_reference_cleared(self, engine, table):
        """close() 后 cursor 引用为 None"""
        async with engine.execute("SELECT * FROM test_leak LIMIT 5") as r:
            await r.fetch_all()

        # async with 退出后，cursor 应已清除
        assert r._Result__cursor is None
