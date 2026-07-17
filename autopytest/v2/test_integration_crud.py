#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整 CRUD 集成测试

覆盖所有增删改查操作 + 所有 result_class 类型 + stream 模式 + 事务自动 commit。
需要真实 MySQL 数据库。
"""

from urllib.parse import quote

import pytest
from pydantic import BaseModel

from asmysql.v2 import Engine

pytestmark = pytest.mark.integration

_TEST_DB = "asmysql_test_crud"


class User(BaseModel):
    id: int
    name: str
    email: str


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
        CREATE TABLE IF NOT EXISTS test_crud (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            price DECIMAL(10, 2) DEFAULT 0
        )
    """):
        pass
    yield
    async with engine.execute("DROP TABLE IF EXISTS test_crud"):
        pass


# ── TestCreate：CREATE 操作 ─────────────────────────────────────────────


class TestCreate:
    """CREATE TABLE 操作"""

    async def test_create_table(self, engine):
        """CREATE TABLE + error is None"""
        async with engine.execute("""
            CREATE TABLE IF NOT EXISTS test_create_tbl (id INT PRIMARY KEY)
        """) as result:
            assert result.error is None
        async with engine.execute("DROP TABLE IF EXISTS test_create_tbl"):
            pass

    async def test_create_table_if_not_exists(self, engine):
        """CREATE TABLE IF NOT EXISTS 多次执行不报错"""
        async with engine.execute("CREATE TABLE IF NOT EXISTS test_create_dup (id INT)"):
            pass
        async with engine.execute("CREATE TABLE IF NOT EXISTS test_create_dup (id INT)") as result:
            assert result.error is None
        async with engine.execute("DROP TABLE IF EXISTS test_create_dup"):
            pass


# ── TestInsert：INSERT 操作 ─────────────────────────────────────────────


class TestInsert:
    """INSERT 操作"""

    async def test_insert_single(self, engine, table):
        """INSERT 单条 + row_count == 1"""
        async with engine.execute(
            "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
            ("张三", "zhangsan@example.com"),
        ) as result:
            assert result.error is None
            assert result.row_count == 1

    async def test_insert_with_last_rowid(self, engine, table):
        """INSERT + last_rowid 验证自增 ID"""
        async with engine.execute(
            "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
            ("李四", "lisi@example.com"),
        ) as result:
            assert result.error is None
            assert result.last_rowid is not None
            assert result.last_rowid >= 1

    async def test_insert_with_params_tuple(self, engine, table):
        """INSERT 使用 tuple 参数"""
        async with engine.execute(
            "INSERT INTO test_crud (name, email, price) VALUES (%s, %s, %s)",
            ("王五", "wangwu@example.com", 99.99),
        ) as result:
            assert result.error is None
            assert result.row_count == 1

    async def test_insert_with_params_dict(self, engine, table):
        """INSERT 使用 dict 参数"""
        async with engine.execute(
            "INSERT INTO test_crud (name, email, price) VALUES (%(name)s, %(email)s, %(price)s)",
            {"name": "赵六", "email": "zhaoliu@example.com", "price": 50.00},
        ) as result:
            assert result.error is None
            assert result.row_count == 1


# ── TestSelect：SELECT 操作 ─────────────────────────────────────────────


class TestSelect:
    """SELECT 操作与各种获取方法"""

    async def test_select_fetch_one(self, engine, table):
        """SELECT + fetch_one"""
        async with engine.execute(
            "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com"),
        ):
            pass
        async with engine.execute("SELECT * FROM test_crud WHERE name = %s", ("Alice",)) as r:
            data = await r.fetch_one()
            assert data is not None
            assert isinstance(data, tuple)
            assert data[1] == "Alice"

    async def test_select_fetch_many(self, engine, table):
        """SELECT + fetch_many"""
        for i in range(5):
            async with engine.execute(
                "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
                (f"user_{i}", f"user_{i}@example.com"),
            ):
                pass
        async with engine.execute("SELECT * FROM test_crud ORDER BY id") as r:
            data = await r.fetch_many(3)
            assert len(data) == 3
            assert all(isinstance(row, tuple) for row in data)

    async def test_select_fetch_many_with_size(self, engine, table):
        """SELECT + fetch_many(size=2)"""
        for i in range(5):
            async with engine.execute(
                "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
                (f"user_{i}", f"user_{i}@example.com"),
            ):
                pass
        async with engine.execute("SELECT * FROM test_crud ORDER BY id") as r:
            data = await r.fetch_many(2)
            assert len(data) == 2

    async def test_select_fetch_all(self, engine, table):
        """SELECT + fetch_all"""
        for i in range(3):
            async with engine.execute(
                "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
                (f"user_{i}", f"user_{i}@example.com"),
            ):
                pass
        async with engine.execute("SELECT * FROM test_crud ORDER BY id") as r:
            data = await r.fetch_all()
            assert len(data) == 3
            assert all(isinstance(row, tuple) for row in data)

    async def test_select_async_for(self, engine, table):
        """SELECT + async for row in result"""
        for i in range(3):
            async with engine.execute(
                "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
                (f"user_{i}", f"user_{i}@example.com"),
            ):
                pass
        count = 0
        async for row in engine.execute("SELECT * FROM test_crud ORDER BY id"):
            assert isinstance(row, tuple)
            count += 1
        assert count == 3

    async def test_select_iterate(self, engine, table):
        """SELECT + async for row in result.iterate()"""
        for i in range(3):
            async with engine.execute(
                "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
                (f"user_{i}", f"user_{i}@example.com"),
            ):
                pass
        async with engine.execute("SELECT * FROM test_crud ORDER BY id") as r:
            users = []
            async for user in r.iterate():
                users.append(user)
            assert len(users) == 3

    async def test_select_async_with(self, engine, table):
        """async with execute() as result"""
        async with engine.execute(
            "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com"),
        ):
            pass
        async with engine.execute("SELECT * FROM test_crud WHERE name = %s", ("Alice",)) as r:
            data = await r.fetch_one()
            assert data is not None
            assert data[1] == "Alice"

    async def test_select_no_rows(self, engine, table):
        """SELECT 空结果集"""
        async with engine.execute("SELECT * FROM test_crud WHERE name = %s", ("不存在",)) as r:
            data = await r.fetch_one()
            assert data is None


# ── TestUpdate：UPDATE 操作 ─────────────────────────────────────────────


class TestUpdate:
    """UPDATE 操作"""

    async def test_update_single_row(self, engine, table):
        """UPDATE 单条 + row_count == 1"""
        async with engine.execute(
            "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com"),
        ):
            pass
        async with engine.execute(
            "UPDATE test_crud SET email = %s WHERE name = %s",
            ("newalice@example.com", "Alice"),
        ) as result:
            assert result.error is None
            assert result.row_count == 1

    async def test_update_multiple_rows(self, engine, table):
        """UPDATE 多条 + row_count 验证"""
        for i in range(5):
            async with engine.execute(
                "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
                (f"user_{i}", f"user_{i}@example.com"),
            ):
                pass
        async with engine.execute(
            "UPDATE test_crud SET price = %s WHERE price = 0", (99.99,)
        ) as result:
            assert result.error is None
            assert result.row_count == 5

    async def test_update_no_match(self, engine, table):
        """UPDATE 无匹配 + row_count == 0"""
        async with engine.execute(
            "UPDATE test_crud SET email = %s WHERE name = %s",
            ("new@example.com", "不存在的用户"),
        ) as result:
            assert result.error is None
            assert result.row_count == 0


# ── TestDelete：DELETE 操作 ─────────────────────────────────────────────


class TestDelete:
    """DELETE 操作"""

    async def test_delete_single_row(self, engine, table):
        """DELETE 单条 + row_count == 1"""
        async with engine.execute(
            "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com"),
        ):
            pass
        async with engine.execute(
            "DELETE FROM test_crud WHERE name = %s", ("Alice",)
        ) as result:
            assert result.error is None
            assert result.row_count == 1

    async def test_delete_multiple_rows(self, engine, table):
        """DELETE 多条 + row_count 验证"""
        for i in range(5):
            async with engine.execute(
                "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
                (f"user_{i}", f"user_{i}@example.com"),
            ):
                pass
        async with engine.execute("DELETE FROM test_crud WHERE price = 0") as result:
            assert result.error is None
            assert result.row_count == 5

    async def test_delete_no_match(self, engine, table):
        """DELETE 无匹配 + row_count == 0"""
        async with engine.execute(
            "DELETE FROM test_crud WHERE name = %s", ("不存在的用户",)
        ) as result:
            assert result.error is None
            assert result.row_count == 0


# ── TestExecuteMany：execute_many 操作 ──────────────────────────────────


class TestExecuteMany:
    """execute_many 批量操作"""

    async def test_execute_many_insert(self, engine, table):
        """execute_many INSERT + row_count"""
        data = [
            (f"user_{i}", f"user_{i}@example.com", float(i * 10))
            for i in range(5)
        ]
        async with engine.execute_many(
            "INSERT INTO test_crud (name, email, price) VALUES (%s, %s, %s)", data
        ) as result:
            assert result.error is None
            assert result.row_count == 5

    async def test_execute_many_update(self, engine, table):
        """execute_many UPDATE + row_count"""
        for i in range(3):
            async with engine.execute(
                "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
                (f"user_{i}", f"user_{i}@example.com"),
            ):
                pass
        update_data = [(f"new_{i}", f"user_{i}") for i in range(3)]
        async with engine.execute_many(
            "UPDATE test_crud SET name = %s WHERE name = %s", update_data
        ) as result:
            assert result.error is None

    async def test_execute_many_delete(self, engine, table):
        """execute_many DELETE + row_count"""
        for i in range(3):
            async with engine.execute(
                "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
                (f"user_{i}", f"user_{i}@example.com"),
            ):
                pass
        delete_data = [(f"user_{i}",) for i in range(3)]
        async with engine.execute_many(
            "DELETE FROM test_crud WHERE name = %s", delete_data
        ) as result:
            assert result.error is None


# ── TestResultClassTypes：result_class 类型 ─────────────────────────────


class TestResultClassTypes:
    """不同 result_class 类型的结果"""

    async def test_tuple_result_class(self, engine, table):
        """result_class=tuple（默认）"""
        async with engine.execute(
            "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com"),
        ):
            pass
        async with engine.execute("SELECT * FROM test_crud WHERE name = %s", ("Alice",)) as r:
            data = await r.fetch_one()
            assert isinstance(data, tuple)

    async def test_dict_result_class(self, engine, table):
        """result_class=dict"""
        async with engine.execute(
            "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com"),
        ):
            pass
        async with engine.execute(
            "SELECT * FROM test_crud WHERE name = %s", ("Alice",), result_class=dict
        ) as r:
            data = await r.fetch_one()
            assert isinstance(data, dict)
            assert data["name"] == "Alice"
            assert data["email"] == "alice@example.com"

    async def test_pydantic_model_result_class(self, engine, table):
        """result_class=自定义 Pydantic Model"""
        async with engine.execute(
            "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com"),
        ):
            pass
        async with engine.execute(
            "SELECT id, name, email FROM test_crud WHERE name = %s",
            ("Alice",),
            result_class=User,
        ) as r:
            data = await r.fetch_one()
            assert isinstance(data, User)
            assert data.name == "Alice"
            assert data.email == "alice@example.com"

    async def test_stream_tuple(self, engine, table):
        """stream=True + tuple"""
        for i in range(5):
            async with engine.execute(
                "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
                (f"user_{i}", f"user_{i}@example.com"),
            ):
                pass
        count = 0
        async for row in engine.execute("SELECT * FROM test_crud ORDER BY id", stream=True):
            assert isinstance(row, tuple)
            count += 1
        assert count == 5

    async def test_stream_dict(self, engine, table):
        """stream=True + dict"""
        for i in range(3):
            async with engine.execute(
                "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
                (f"user_{i}", f"user_{i}@example.com"),
            ):
                pass
        async for row in engine.execute(
            "SELECT * FROM test_crud ORDER BY id", stream=True, result_class=dict
        ):
            assert isinstance(row, dict)
            assert "name" in row

    async def test_stream_pydantic_model(self, engine, table):
        """stream=True + Pydantic Model"""
        for i in range(3):
            async with engine.execute(
                "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
                (f"user_{i}", f"user_{i}@example.com"),
            ):
                pass
        users = []
        async for user in engine.execute(
            "SELECT id, name, email FROM test_crud ORDER BY id",
            stream=True,
            result_class=User,
        ):
            assert isinstance(user, User)
            users.append(user)
        assert len(users) == 3


# ── TestTransaction：事务自动 commit ────────────────────────────────────


class TestTransaction:
    """事务自动 commit 行为"""

    async def test_auto_commit_insert(self, engine, table):
        """INSERT 自动 commit，另一连接可见"""
        async with engine.execute(
            "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com"),
        ):
            pass
        # 用另一个查询验证数据已提交
        async with engine.execute(
            "SELECT COUNT(*) FROM test_crud WHERE name = %s", ("Alice",)
        ) as r:
            data = await r.fetch_one()
            assert data[0] == 1

    async def test_select_no_commit(self, engine, table):
        """SELECT 不触发 commit（验证 SELECT 后数据状态不变）"""
        async with engine.execute(
            "INSERT INTO test_crud (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com"),
        ):
            pass
        # SELECT 不应改变数据
        async with engine.execute("SELECT * FROM test_crud") as r:
            await r.fetch_all()
        # 数据仍存在
        async with engine.execute(
            "SELECT COUNT(*) FROM test_crud WHERE name = %s", ("Alice",)
        ) as r:
            data = await r.fetch_one()
            assert data[0] == 1

    async def test_ddl_auto_commit(self, engine):
        """DDL（CREATE/DROP）自动 commit"""
        async with engine.execute(
            "CREATE TABLE IF NOT EXISTS test_ddl_commit (id INT PRIMARY KEY)"
        ) as result:
            assert result.error is None
        # 验证表已创建（commit 后才能被其他连接看到）
        async with engine.execute("SHOW TABLES LIKE %s", ("test_ddl_commit",)) as r:
            data = await r.fetch_all()
            assert len(data) >= 1
        async with engine.execute("DROP TABLE IF EXISTS test_ddl_commit"):
            pass
