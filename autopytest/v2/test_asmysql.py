#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""集成测试 — 需要真实 MySQL 数据库"""

import pytest
from pydantic import BaseModel

from asmysql.v2 import AsMysql, Engine

pytestmark = pytest.mark.integration


class User(BaseModel):
    id: int
    name: str
    email: str


class Product(BaseModel):
    id: int
    name: str
    price: float


@pytest.fixture
async def engine():
    """创建并连接 Engine，测试结束后断开连接"""
    eng = Engine("mysql://root:password@localhost:3306/test_db")
    try:
        await eng.connect()
    except ConnectionError:
        pytest.skip("MySQL 数据库不可用，跳过集成测试")
    yield eng
    await eng.disconnect()


@pytest.fixture
def asmysql(engine):
    """创建使用真实 Engine 的 AsMysql 实例"""
    return AsMysql(engine)


# ── 测试 ─────────────────────────────────────────────────────────────


async def test_asmysql_creation(asmysql, engine):
    """测试 AsMysql 实例创建"""
    assert isinstance(asmysql, AsMysql)
    assert asmysql.client == engine
    assert str(asmysql) == f"AsMysql={engine.url}"
    assert "AsMysql" in repr(asmysql)


async def test_asmysql_client_property(asmysql, engine):
    """测试 AsMysql 的 client 属性"""
    client = asmysql.client
    assert client == engine
    assert hasattr(client, "execute")
    assert hasattr(client, "execute_many")
    assert hasattr(client, "is_connected")


async def test_asmysql_execute_query_with_different_result_types(asmysql):
    """测试 AsMysql 执行查询语句的不同结果类型"""
    # 创建测试表
    create_table = """
    CREATE TABLE IF NOT EXISTS test_users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL
    )
    """
    result = await asmysql.client.execute(create_table)
    assert result.error is None

    # 插入测试数据
    insert_query = "INSERT INTO test_users (name, email) VALUES (%s, %s)"
    result = await asmysql.client.execute(insert_query, ("张三", "zhangsan@example.com"))
    assert result.error is None
    assert result.row_count == 1

    # 测试默认 tuple 结果类型
    select_query = "SELECT * FROM test_users WHERE name = %s"
    result = await asmysql.client.execute(select_query, ("张三",))
    assert result.error is None

    # 测试 async for row in result
    count = 0
    async for row in result:
        count += 1
        assert isinstance(row, tuple)
        assert len(row) == 3  # id, name, email
    assert count == 1

    # 重新执行查询以测试其他方法
    result = await asmysql.client.execute(select_query, ("张三",))

    # 测试 fetch_one
    data = await result.fetch_one()
    assert data is not None
    assert isinstance(data, tuple)
    assert data[1] == "张三"
    assert data[2] == "zhangsan@example.com"

    # 再次插入数据以测试更多方法
    result = await asmysql.client.execute(insert_query, ("李四", "lisi@example.com"))
    assert result.error is None

    # 重新执行查询以测试 fetch_many
    result = await asmysql.client.execute(select_query.replace("= %s", "!= %s"), ("不存在的用户",))
    data = await result.fetch_many(1)
    assert data is not None
    assert len(data) == 1
    assert isinstance(data[0], tuple)

    # 测试 fetch_all
    result = await asmysql.client.execute("SELECT * FROM test_users ORDER BY id")
    data = await result.fetch_all()
    assert data is not None
    assert len(data) == 2
    assert isinstance(data[0], tuple)
    assert isinstance(data[1], tuple)

    # 测试 dict 结果类型
    result = await asmysql.client.execute(select_query, ("张三",), result_class=dict)
    data = await result.fetch_one()
    assert data is not None
    assert isinstance(data, dict)
    assert data["name"] == "张三"
    assert data["email"] == "zhangsan@example.com"

    # 测试自定义模型结果类型
    result = await asmysql.client.execute(select_query, ("张三",), result_class=User)
    data = await result.fetch_one()
    assert data is not None
    assert isinstance(data, User)
    assert data.name == "张三"
    assert data.email == "zhangsan@example.com"

    # 测试 async for item in result.iterate()
    result = await asmysql.client.execute("SELECT * FROM test_users", result_class=User)
    users = []
    async for item in result.iterate():
        users.append(item)
    assert len(users) == 2
    assert isinstance(users[0], User)
    assert isinstance(users[1], User)

    # 测试 async with self.client.execute(...) as result
    async with asmysql.client.execute(select_query, ("张三",), result_class=User) as result:
        user_data = None
        async for item in result.iterate():
            user_data = item
        assert isinstance(user_data, User)
        assert user_data.name == "张三"

    # 清理测试数据
    drop_table = "DROP TABLE IF EXISTS test_users"
    result = await asmysql.client.execute(drop_table)
    assert result.error is None


async def test_asmysql_execute_many(asmysql):
    """测试 AsMysql 批量执行语句"""
    # 创建测试表
    create_table = """
    CREATE TABLE IF NOT EXISTS test_products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        price DECIMAL(10, 2) NOT NULL
    )
    """
    result = await asmysql.client.execute(create_table)
    assert result.error is None

    # 批量插入数据
    insert_query = "INSERT INTO test_products (name, price) VALUES (%s, %s)"
    products_data = [("产品1", 100.00), ("产品2", 200.00), ("产品3", 300.00)]
    result = await asmysql.client.execute_many(insert_query, products_data)
    assert result.error is None
    assert result.row_count == 3

    # 查询所有数据
    select_query = "SELECT * FROM test_products ORDER BY id"
    result = await asmysql.client.execute(select_query, result_class=dict)
    data = await result.fetch_all()
    assert len(data) == 3
    assert data[0]["name"] == "产品1"
    assert data[1]["price"] == 200.00
    assert data[2]["name"] == "产品3"

    # 测试 execute_many 与自定义模型
    result = await asmysql.client.execute(select_query, result_class=Product)
    products = []
    async for product in result.iterate():
        products.append(product)
    assert len(products) == 3
    assert isinstance(products[0], Product)
    assert isinstance(products[1], Product)
    assert isinstance(products[2], Product)

    # 测试 execute_many 与 async with
    async with asmysql.client.execute(select_query, result_class=Product) as result:
        product_list = []
        async for item in result.iterate():
            product_list.append(item)
        assert len(product_list) == 3
        assert isinstance(product_list[0], Product)

    # 清理测试数据
    drop_table = "DROP TABLE IF EXISTS test_products"
    result = await asmysql.client.execute(drop_table)
    assert result.error is None


async def test_asmysql_execute_streaming(asmysql):
    """测试 AsMysql 流式执行查询"""
    # 创建测试表
    create_table = """
    CREATE TABLE IF NOT EXISTS test_stream (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL
    )
    """
    result = await asmysql.client.execute(create_table)
    assert result.error is None

    # 插入测试数据
    insert_query = "INSERT INTO test_stream (name) VALUES (%s)"
    data_to_insert = [("数据" + str(i),) for i in range(10)]
    result = await asmysql.client.execute_many(insert_query, data_to_insert)
    assert result.error is None
    assert result.row_count == 10

    # 测试流式查询
    select_query = "SELECT * FROM test_stream"
    result = await asmysql.client.execute(select_query, stream=True)
    assert result.error is None
    assert result.row_count is None  # 流式查询应该返回 None

    # 测试流式查询的 async for
    count = 0
    async for row in result:
        count += 1
        assert isinstance(row, tuple)
    assert count == 10

    # 清理测试数据
    drop_table = "DROP TABLE IF EXISTS test_stream"
    result = await asmysql.client.execute(drop_table)
    assert result.error is None


async def test_asmysql_direct_async_for_on_execute(asmysql):
    """测试直接在 execute 返回结果上使用 async for 迭代"""
    # 创建测试表
    create_table = """
    CREATE TABLE IF NOT EXISTS test_direct_iteration (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL
    )
    """
    await asmysql.client.execute(create_table)

    # 插入测试数据
    insert_query = "INSERT INTO test_direct_iteration (name, email) VALUES (%s, %s)"
    test_users = [("张三", "zhangsan@example.com"), ("李四", "lisi@example.com"), ("王五", "wangwu@example.com")]

    for user in test_users:
        await asmysql.client.execute(insert_query, user)

    # 测试直接在 execute 返回结果上使用 async for 迭代
    select_query = "SELECT * FROM test_direct_iteration"

    # 测试使用 tuple 类型
    users = []
    async for user in asmysql.client.execute(select_query):
        users.append(user)
        assert isinstance(user, tuple)
    assert len(users) == 3

    # 测试使用 dict 类型
    users_dict = []
    async for user in asmysql.client.execute(select_query, result_class=dict):
        users_dict.append(user)
        assert isinstance(user, dict)
    assert len(users_dict) == 3

    # 测试使用自定义模型类型
    users_model = []
    async for user in asmysql.client.execute(select_query, result_class=User):
        users_model.append(user)
        assert isinstance(user, User)
    assert len(users_model) == 3

    # 清理测试数据
    await asmysql.client.execute("DROP TABLE IF EXISTS test_direct_iteration")
