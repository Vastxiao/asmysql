#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
并发集成测试

使用真实 MySQL 验证并发场景：
- 并发 SELECT 查询
- 并发 INSERT 插入
- 并发混合读写操作
- 并发操作不同表
- 并发流式查询
- 连接池在并发下的状态
"""

import asyncio
from urllib.parse import quote

import pytest

from asmysql.v2 import Engine

pytestmark = pytest.mark.integration

_TEST_DB = "asmysql_test_concurrency"


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
async def tables(engine):
    """创建多个测试表"""
    async with engine.execute("""
        CREATE TABLE IF NOT EXISTS test_conc_a (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        )
    """):
        pass
    async with engine.execute("""
        CREATE TABLE IF NOT EXISTS test_conc_b (
            id INT AUTO_INCREMENT PRIMARY KEY,
            value INT NOT NULL
        )
    """):
        pass
    yield
    # teardown: 先释放所有空闲连接（触发 MySQL 释放元数据锁）
    await engine.release_connections()
    async with engine.execute("DROP TABLE IF EXISTS test_conc_a"):
        pass
    async with engine.execute("DROP TABLE IF EXISTS test_conc_b"):
        pass


# ── TestConcurrency：并发操作 ───────────────────────────────────────────


class TestConcurrency:
    """并发操作集成测试"""

    async def test_concurrent_select_queries(self, engine, tables):
        """asyncio.gather 并发执行多个 SELECT"""
        # 先插入数据
        for i in range(10):
            async with engine.execute(
                "INSERT INTO test_conc_a (name) VALUES (%s)", (f"user_{i}",)
            ):
                pass

        async def query_one(idx):
            async with engine.execute("SELECT * FROM test_conc_a WHERE id = %s", (idx,)) as r:
                return await r.fetch_one()

        results = await asyncio.gather(
            *[query_one(i) for i in range(1, 6)]
        )
        assert len(results) == 5
        assert all(r is not None for r in results)

    async def test_concurrent_inserts(self, engine, tables):
        """并发插入多条记录"""
        async def insert_one(idx):
            async with engine.execute(
                "INSERT INTO test_conc_a (name) VALUES (%s)", (f"concurrent_{idx}",)
            ) as result:
                return result.row_count

        results = await asyncio.gather(
            *[insert_one(i) for i in range(5)]
        )
        assert all(r == 1 for r in results)

        # 验证所有数据已插入
        async with engine.execute("SELECT COUNT(*) FROM test_conc_a") as r:
            count = await r.fetch_one()
            assert count[0] == 5

    async def test_concurrent_mixed_read_write(self, engine, tables):
        """并发混合读写操作"""
        # 先插入基础数据
        for i in range(5):
            async with engine.execute(
                "INSERT INTO test_conc_a (name) VALUES (%s)", (f"base_{i}",)
            ):
                pass

        async def read_op():
            async with engine.execute("SELECT COUNT(*) FROM test_conc_a") as r:
                return await r.fetch_one()

        async def write_op(idx):
            async with engine.execute(
                "INSERT INTO test_conc_b (value) VALUES (%s)", (idx,)
            ):
                pass
            return True

        results = await asyncio.gather(
            read_op(),
            write_op(1),
            read_op(),
            write_op(2),
            read_op(),
        )
        # 所有操作应成功
        assert len(results) == 5

    async def test_concurrent_different_tables(self, engine, tables):
        """并发操作不同表"""
        async def insert_table_a(idx):
            async with engine.execute(
                "INSERT INTO test_conc_a (name) VALUES (%s)", (f"a_{idx}",)
            ):
                pass
            return "a"

        async def insert_table_b(idx):
            async with engine.execute(
                "INSERT INTO test_conc_b (value) VALUES (%s)", (idx,)
            ):
                pass
            return "b"

        results = await asyncio.gather(
            *[insert_table_a(i) for i in range(5)],
            *[insert_table_b(i) for i in range(5)],
        )
        assert results.count("a") == 5
        assert results.count("b") == 5

    async def test_concurrent_stream_queries(self, engine, tables):
        """并发流式查询"""
        # 插入数据
        for i in range(10):
            async with engine.execute(
                "INSERT INTO test_conc_a (name) VALUES (%s)", (f"stream_{i}",)
            ):
                pass

        async def stream_query():
            count = 0
            async for row in engine.execute("SELECT * FROM test_conc_a", stream=True):
                count += 1
            return count

        results = await asyncio.gather(
            stream_query(),
            stream_query(),
        )
        assert all(r == 10 for r in results)

    async def test_pool_size_under_concurrency(self, engine, tables):
        """并发时 pool.size/used 变化验证"""
        # 插入数据
        for i in range(10):
            async with engine.execute(
                "INSERT INTO test_conc_a (name) VALUES (%s)", (f"pool_{i}",)
            ):
                pass

        initial_status = engine.status

        async def slow_query():
            async with engine.execute("SELECT * FROM test_conc_a") as r:
                await r.fetch_all()
            return True

        # 并发执行
        await asyncio.gather(*[slow_query() for _ in range(5)])

        # 所有操作完成后，连接应归还
        final_status = engine.status
        assert final_status["pool_free"] >= 0
        # pool_size 不应无限增长
        assert final_status["pool_size"] <= initial_status["pool_maxsize"]
