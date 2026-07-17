# -*- coding: utf-8 -*-

"""
AsMysql 薄封装层 Mock 测试

仅测试 AsMysql 类本身的实例化与 client 属性，
不重复 Engine/Result 的功能测试（分别在 test_mock_engine.py / test_mock_result.py 中）。
"""

from unittest.mock import AsyncMock, Mock

from pydantic import BaseModel

from asmysql.v2 import AsMysql


class User(BaseModel):
    id: int
    name: str
    email: str


# ── 同步测试 ─────────────────────────────────────────────────────────


def test_asmysql_creation(asmysql, mock_engine):
    """测试 AsMysql 实例创建"""
    assert isinstance(asmysql, AsMysql)
    assert asmysql.client == mock_engine
    assert str(asmysql) == "AsMysql=mysql://root@localhost:3306/"
    assert "AsMysql" in repr(asmysql)


def test_asmysql_client_property(asmysql, mock_engine):
    """测试 AsMysql 的 client 属性"""
    client = asmysql.client
    assert client == mock_engine
    assert hasattr(client, "execute")
    assert hasattr(client, "execute_many")
    assert hasattr(client, "is_connected")


def test_asmysql_execute_query(asmysql, mock_result):
    """测试 AsMysql 执行查询语句"""
    asmysql.client.execute = Mock(return_value=mock_result)

    query = "SELECT * FROM test_users WHERE name = %s"
    result = asmysql.client.execute(query, ("张三",))

    asmysql.client.execute.assert_called_once_with(query, ("张三",))
    assert result == mock_result


def test_asmysql_execute_many(asmysql, mock_result):
    """测试 AsMysql 批量执行语句"""
    mock_result.row_count = 3
    asmysql.client.execute_many = Mock(return_value=mock_result)

    query = "INSERT INTO test_products (name, price) VALUES (%s, %s)"
    products_data = [("产品1", 100.00), ("产品2", 200.00), ("产品3", 300.00)]
    result = asmysql.client.execute_many(query, products_data)

    asmysql.client.execute_many.assert_called_once_with(query, products_data)
    assert result == mock_result


def test_asmysql_execute_with_different_result_types(asmysql, mock_result):
    """测试 AsMysql 执行查询语句的不同结果类型"""
    asmysql.client.execute = Mock(return_value=mock_result)

    query = "SELECT * FROM test_users WHERE name = %s"

    # 测试 dict 结果类型
    result = asmysql.client.execute(query, ("张三",), result_class=dict)
    asmysql.client.execute.assert_called_with(query, ("张三",), result_class=dict)
    assert result == mock_result

    # 测试自定义模型结果类型
    result = asmysql.client.execute(query, ("张三",), result_class=User)
    asmysql.client.execute.assert_called_with(query, ("张三",), result_class=User)
    assert result == mock_result


def test_asmysql_execute_streaming(asmysql, mock_result):
    """测试 AsMysql 流式执行查询"""
    mock_result.row_count = None
    asmysql.client.execute = Mock(return_value=mock_result)

    query = "SELECT * FROM test_users"
    result = asmysql.client.execute(query, stream=True)

    asmysql.client.execute.assert_called_with(query, stream=True)
    assert result == mock_result


def test_asmysql_execute_with_async_context_manager(asmysql, mock_result):
    """测试 AsMysql 执行查询语句的 async with 语句"""
    mock_result.__aenter__ = AsyncMock(return_value=mock_result)
    mock_result.__aexit__ = AsyncMock(return_value=None)
    asmysql.client.execute = Mock(return_value=mock_result)

    query = "SELECT * FROM test_users WHERE name = %s"
    result = asmysql.client.execute(query, ("张三",))

    asmysql.client.execute.assert_called_once_with(query, ("张三",))
    assert result == mock_result


# ── 异步测试 ─────────────────────────────────────────────────────────


async def test_asmysql_execute_async_for_iteration(asmysql, mock_result):
    """测试 AsMysql 执行查询语句的 async for 迭代"""
    mock_result.__aiter__ = Mock(return_value=mock_result)
    mock_result.__anext__ = AsyncMock(
        side_effect=[("张三", "zhangsan@example.com"), ("李四", "lisi@example.com"), StopAsyncIteration]
    )
    asmysql.client.execute = Mock(return_value=mock_result)

    query = "SELECT name, email FROM test_users"
    result = asmysql.client.execute(query)

    asmysql.client.execute.assert_called_once_with(query)
    assert result == mock_result

    users = []
    async for user in result:
        users.append(user)

    assert len(users) == 2
    assert users[0] == ("张三", "zhangsan@example.com")
    assert users[1] == ("李四", "lisi@example.com")


async def test_asmysql_execute_iterate_method(asmysql, mock_result):
    """测试 AsMysql 执行查询语句的 iterate 方法"""
    async def mock_iterate():
        for item in [("张三", "zhangsan@example.com"), ("李四", "lisi@example.com")]:
            yield item

    mock_result.iterate = Mock(return_value=mock_iterate())
    asmysql.client.execute = Mock(return_value=mock_result)

    query = "SELECT name, email FROM test_users"
    result = asmysql.client.execute(query)

    asmysql.client.execute.assert_called_once_with(query)
    assert result == mock_result

    users = []
    async for user in result.iterate():
        users.append(user)

    assert len(users) == 2
    assert users[0] == ("张三", "zhangsan@example.com")
    assert users[1] == ("李四", "lisi@example.com")


async def test_asmysql_direct_async_for_on_execute_mock(asmysql, mock_result):
    """测试使用 mock 直接在 execute 返回结果上使用 async for 迭代"""
    mock_result.__aiter__ = Mock(return_value=mock_result)
    mock_result.__anext__ = AsyncMock(
        side_effect=[("张三", "zhangsan@example.com"), ("李四", "lisi@example.com"), StopAsyncIteration]
    )
    asmysql.client.execute = Mock(return_value=mock_result)

    query = "SELECT name, email FROM test_users"
    result = asmysql.client.execute(query, result_class=User)

    asmysql.client.execute.assert_called_once_with(query, result_class=User)
    assert result == mock_result

    users = []
    async for user in result:
        users.append(user)

    assert len(users) == 2
    assert users[0] == ("张三", "zhangsan@example.com")
    assert users[1] == ("李四", "lisi@example.com")
