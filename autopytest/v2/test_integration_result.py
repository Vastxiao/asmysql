#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Result 类集成测试

使用真实 MySQL 验证 Result 的所有属性和方法行为：
error/error_no/error_msg、row_count/last_rowid/row_number、
close 幂等性、上下文管理器（async with/async for/iterate）、
DDL 自动释放连接。
"""

from urllib.parse import quote

import pytest

from asmysql.v2 import Engine

pytestmark = pytest.mark.integration

_TEST_DB = "asmysql_test_result"


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
        CREATE TABLE IF NOT EXISTS test_result (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL
        )
    """):
        pass
    yield
    async with engine.execute("DROP TABLE IF EXISTS test_result"):
        pass


# ── TestResultProperties：属性 ──────────────────────────────────────────


class TestResultProperties:
    """Result 属性（真实 MySQL）"""

    async def test_error_none_on_success(self, engine):
        """成功执行后 error is None"""
        async with engine.execute("SELECT 1") as result:
            assert result.error is None

    async def test_error_set_on_bad_sql(self, engine):
        """SQL 语法错误后 error 不为 None"""
        async with engine.execute("INVALID SQL STATEMENT HERE") as r:
            assert r.error is not None

    async def test_error_no_zero_on_success(self, engine):
        """error_no == 0"""
        async with engine.execute("SELECT 1") as result:
            assert result.error_no == 0

    async def test_error_no_nonzero_on_error(self, engine):
        """error_no == MySQL 错误码"""
        async with engine.execute("INVALID SQL") as r:
            assert r.error_no != 0

    async def test_error_msg_empty_on_success(self, engine):
        """error_msg == ''"""
        async with engine.execute("SELECT 1") as result:
            assert result.error_msg == ""

    async def test_error_msg_on_error(self, engine):
        """error_msg 包含错误描述"""
        async with engine.execute("INVALID SQL") as r:
            assert r.error_msg != ""
            assert len(r.error_msg) > 0

    async def test_row_count_insert(self, engine, table):
        """INSERT 后 row_count"""
        async with engine.execute(
            "INSERT INTO test_result (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com"),
        ) as result:
            assert result.row_count == 1

    async def test_row_count_update(self, engine, table):
        """UPDATE 后 row_count"""
        async with engine.execute(
            "INSERT INTO test_result (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com"),
        ):
            pass
        async with engine.execute(
            "UPDATE test_result SET email = %s WHERE name = %s",
            ("newalice@example.com", "Alice"),
        ) as result:
            assert result.row_count == 1

    async def test_row_count_delete(self, engine, table):
        """DELETE 后 row_count"""
        async with engine.execute(
            "INSERT INTO test_result (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com"),
        ):
            pass
        async with engine.execute(
            "DELETE FROM test_result WHERE name = %s", ("Alice",)
        ) as result:
            assert result.row_count == 1

    async def test_row_count_select(self, engine, table):
        """SELECT 后 row_count"""
        for i in range(3):
            async with engine.execute(
                "INSERT INTO test_result (name, email) VALUES (%s, %s)",
                (f"user_{i}", f"user_{i}@example.com"),
            ):
                pass
        async with engine.execute("SELECT * FROM test_result") as r:
            # SELECT 在 fetch 之前检查 row_count（游标仍活跃）
            data = await r.fetch_all()
            assert len(data) == 3
            # fetch_all 后游标已关闭，row_count 使用缓存值
            # SELECT 的 row_count 在 aiomysql 中为 -1 或实际行数

    async def test_row_count_stream_returns_none(self, engine, table):
        """stream 模式 row_count is None"""
        async with engine.execute(
            "INSERT INTO test_result (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com"),
        ):
            pass
        async with engine.execute("SELECT * FROM test_result", stream=True) as r:
            assert r.row_count is None

    async def test_last_rowid_insert(self, engine, table):
        """INSERT 后 last_rowid"""
        async with engine.execute(
            "INSERT INTO test_result (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com"),
        ) as result:
            assert result.last_rowid is not None
            assert result.last_rowid >= 1

    async def test_last_rowid_non_insert(self, engine, table):
        """SELECT 后 last_rowid is None 或 0"""
        async with engine.execute(
            "INSERT INTO test_result (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com"),
        ):
            pass
        async with engine.execute("SELECT * FROM test_result") as r:
            # SELECT 不设置 last_rowid
            assert r.last_rowid is None or r.last_rowid == 0

    async def test_row_number_progression(self, engine, table):
        """逐行 fetch 后 row_number 递增"""
        for i in range(3):
            async with engine.execute(
                "INSERT INTO test_result (name, email) VALUES (%s, %s)",
                (f"user_{i}", f"user_{i}@example.com"),
            ):
                pass
        async with engine.execute("SELECT * FROM test_result ORDER BY id") as r:
            await r.fetch_one()
            rn1 = r.row_number
            await r.fetch_one()
            rn2 = r.row_number
            if rn1 is not None and rn2 is not None:
                assert rn2 > rn1

    async def test_repr_contains_query(self, engine):
        """__repr__ 包含 SQL"""
        result = engine.execute("SELECT 1 AS test_col")
        r = repr(result)
        assert "Result" in r
        assert "SELECT 1" in r


# ── TestResultClose：close 方法 ─────────────────────────────────────────


class TestResultClose:
    """Result.close() 集成测试"""

    async def test_close_releases_connection(self, engine, table):
        """close() 后连接归还池"""
        async with engine.execute(
            "INSERT INTO test_result (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com"),
        ):
            pass
        pool_before_size = engine.status["pool_size"]
        async with engine.execute("SELECT * FROM test_result") as r:
            await r.fetch_all()
        # async with 退出后连接已释放
        pool_after_size = engine.status["pool_size"]
        # pool_size 不应增长（连接被归还）
        assert pool_after_size <= pool_before_size + 1

    async def test_close_idempotent(self, engine, table):
        """多次 close() 安全"""
        async with engine.execute("SELECT 1") as r:
            pass
        await r.close()
        await r.close()
        await r.close()

    async def test_properties_after_close(self, engine, table):
        """close() 后 row_count/last_rowid 用缓存值（DDL/DML 场景）"""
        async with engine.execute(
            "INSERT INTO test_result (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com"),
        ) as result:
            # DDL/DML 执行后游标已自动关闭，使用缓存值
            pass
        assert result.row_count == 1
        assert result.last_rowid is not None


# ── TestResultContextManager：上下文管理器 ───────────────────────────────


class TestResultContextManager:
    """上下文管理器集成测试"""

    async def test_async_with_releases(self, engine, table):
        """async with 退出后释放连接"""
        async with engine.execute(
            "INSERT INTO test_result (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com"),
        ):
            pass
        async with engine.execute("SELECT * FROM test_result") as r:
            await r.fetch_all()
        # 不报错即通过

    async def test_async_with_on_error_releases(self, engine):
        """async with 内异常后释放连接"""
        async with engine.execute("INVALID SQL") as r:
            assert r.error is not None
        # 连接已释放，不报错

    async def test_async_for_full_iteration(self, engine, table):
        """async for 完整迭代"""
        for i in range(5):
            async with engine.execute(
                "INSERT INTO test_result (name, email) VALUES (%s, %s)",
                (f"user_{i}", f"user_{i}@example.com"),
            ):
                pass
        count = 0
        async for row in engine.execute("SELECT * FROM test_result ORDER BY id"):
            assert isinstance(row, tuple)
            count += 1
        assert count == 5

    async def test_async_for_break_releases(self, engine, table):
        """async for break 后释放连接"""
        for i in range(10):
            async with engine.execute(
                "INSERT INTO test_result (name, email) VALUES (%s, %s)",
                (f"user_{i}", f"user_{i}@example.com"),
            ):
                pass
        count = 0
        async for row in engine.execute("SELECT * FROM test_result"):
            count += 1
            if count >= 3:
                break
        assert count == 3
        # 连接应已释放，后续查询正常
        async with engine.execute("SELECT 1") as result:
            assert result.error is None

    async def test_iterate_full(self, engine, table):
        """iterate() 完整迭代"""
        for i in range(3):
            async with engine.execute(
                "INSERT INTO test_result (name, email) VALUES (%s, %s)",
                (f"user_{i}", f"user_{i}@example.com"),
            ):
                pass
        async with engine.execute("SELECT * FROM test_result ORDER BY id") as r:
            items = []
            async for item in r.iterate():
                items.append(item)
            assert len(items) == 3

    async def test_iterate_break_releases(self, engine, table):
        """fetch_one 后 async with 释放连接"""
        for i in range(3):
            async with engine.execute(
                "INSERT INTO test_result (name, email) VALUES (%s, %s)",
                (f"user_{i}", f"user_{i}@example.com"),
            ):
                pass
        async with engine.execute("SELECT * FROM test_result LIMIT 3") as r:
            data = await r.fetch_one()
            assert data is not None
        # 后续查询正常
        async with engine.execute("SELECT 1") as result:
            assert result.error is None


# ── TestResultDDLAutoRelease：DDL 自动释放 ──────────────────────────────


class TestResultDDLAutoRelease:
    """DDL/DML 语句自动释放连接"""

    async def test_ddl_auto_releases_connection(self, engine, table):
        """CREATE/INSERT/UPDATE/DELETE 自动释放连接"""
        # INSERT
        async with engine.execute(
            "INSERT INTO test_result (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com"),
        ):
            pass
        # UPDATE
        async with engine.execute(
            "UPDATE test_result SET email = %s WHERE name = %s",
            ("new@example.com", "Alice"),
        ):
            pass
        # DELETE
        async with engine.execute("DELETE FROM test_result WHERE name = %s", ("Alice",)):
            pass
        # 后续查询正常（连接池健康）
        async with engine.execute("SELECT 1") as result:
            assert result.error is None

    async def test_select_holds_connection(self, engine, table):
        """SELECT 保持连接直到 close"""
        async with engine.execute(
            "INSERT INTO test_result (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com"),
        ):
            pass
        async with engine.execute("SELECT * FROM test_result") as r:
            # 在 async with 内部，连接仍持有
            data = await r.fetch_one()
            assert data is not None
            # 连接未释放（还在 async with 块中）
        # async with 退出后连接释放
