# -*- coding: utf-8 -*-

"""
Engine 类全量 Mock 测试

覆盖 Engine 所有公开 API：初始化、URL 解析、连接管理、属性、execute/execute_many。
全部使用 Mock，无需真实 MySQL 数据库。
"""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from asmysql.v2 import Engine, Result

# ── TestEngineInit：初始化与 URL 解析 ───────────────────────────────────


class TestEngineInit:
    """Engine 构造函数与 URL 解析"""

    def test_default_attributes(self):
        """所有类属性默认值正确"""
        engine = Engine()
        assert engine.host == "127.0.0.1"
        assert engine.port == 3306
        assert engine.user == ""
        assert engine.password == ""
        assert engine.charset == "utf8mb4"
        assert engine.min_pool_size == 1
        assert engine.max_pool_size == 10
        assert engine.pool_recycle == -1
        assert engine.connect_timeout == 5
        assert engine.echo_sql_log is False
        assert engine.result_class is tuple
        assert engine.init_sql is None

    def test_kwargs_override(self):
        """关键字参数覆盖默认值"""
        engine = Engine(
            host="db.example.com",
            port=3307,
            user="admin",
            password="secret",
            charset="utf8",
            min_pool_size=2,
            max_pool_size=20,
            pool_recycle=300.0,
            connect_timeout=10,
            echo_sql_log=True,
            result_class=dict,
            init_sql="SET time_zone = '+00:00'",
        )
        assert engine.host == "db.example.com"
        assert engine.port == 3307
        assert engine.user == "admin"
        assert engine.password == "secret"
        assert engine.charset == "utf8"
        assert engine.min_pool_size == 2
        assert engine.max_pool_size == 20
        assert engine.pool_recycle == 300.0
        assert engine.connect_timeout == 10
        assert engine.echo_sql_log is True
        assert engine.result_class is dict
        assert engine.init_sql == "SET time_zone = '+00:00'"

    def test_url_parsing_basic(self):
        """URL 基本解析"""
        engine = Engine(url="mysql://admin:secret@db.example.com:3307/")
        assert engine.host == "db.example.com"
        assert engine.port == 3307
        assert engine.user == "admin"
        assert engine.password == "secret"

    def test_url_parsing_special_chars(self):
        """URL 密码含特殊字符（@/:）需 URL 编码"""
        # 密码 p@ss:word/123 编码为 p%40ss%3Aword%2F123
        engine = Engine(url="mysql://admin:p%40ss%3Aword%2F123@host:3306/")
        assert engine.user == "admin"
        assert engine.password == "p@ss:word/123"

    def test_url_parsing_query_params(self):
        """URL query 参数（所有支持的参数）"""
        url = (
            "mysql://u:p@host:3306/"
            "?charset=utf8"
            "&min_pool_size=2"
            "&max_pool_size=20"
            "&pool_recycle=300"
            "&connect_timeout=10"
            "&echo_sql_log=true"
            "&init_sql=SET+foo=1"
        )
        engine = Engine(url=url)
        assert engine.charset == "utf8"
        assert engine.min_pool_size == 2
        assert engine.max_pool_size == 20
        assert engine.pool_recycle == 300.0
        assert engine.connect_timeout == 10
        assert engine.echo_sql_log is True
        assert engine.init_sql == "SET foo=1"

    def test_url_invalid_scheme(self):
        """非法 scheme 抛 ValueError"""
        with pytest.raises(ValueError, match="Invalid url scheme"):
            Engine(url="postgresql://u:p@host:5432/")

    def test_url_port_default(self):
        """URL 缺省端口使用默认值 3306"""
        engine = Engine(url="mysql://u:p@host/")
        assert engine.port == 3306

    def test_url_echo_sql_log_false_values(self):
        """URL echo_sql_log 非 true 值为 False"""
        engine = Engine(url="mysql://u:p@host:3306/?echo_sql_log=false")
        assert engine.echo_sql_log is False
        engine2 = Engine(url="mysql://u:p@host:3306/?echo_sql_log=0")
        assert engine2.echo_sql_log is False

    def test_result_class_default(self):
        """result_class 默认 tuple"""
        engine = Engine()
        assert engine.result_class is tuple

    def test_result_class_override(self):
        """result_class 自定义"""
        engine = Engine(result_class=dict)
        assert engine.result_class is dict


# ── TestEngineConnection：连接管理 ────────────────────────────────────


class TestEngineConnection:
    """Engine 连接/断开生命周期"""

    async def test_connect_creates_pool(self):
        """connect() 创建连接池"""
        from autopytest.v2.conftest import make_mock_pool

        pool = make_mock_pool()
        with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=pool)):
            engine = Engine(host="127.0.0.1", port=3306)
            await engine.connect()
            assert engine.is_connected

    async def test_connect_idempotent(self):
        """多次 connect() 幂等，只创建一个池"""
        from autopytest.v2.conftest import make_mock_pool

        pool = make_mock_pool()
        create_count = 0

        async def mock_create(**kw):
            nonlocal create_count
            create_count += 1
            return pool

        with patch("asmysql.v2._engine.create_pool", new=mock_create):
            engine = Engine(host="127.0.0.1", port=3306)
            await engine.connect()
            await engine.connect()
            await engine.connect()
            assert create_count == 1

    async def test_disconnect_closes_pool(self):
        """disconnect() 关闭池并置空"""
        from autopytest.v2.conftest import make_mock_pool

        pool = make_mock_pool()
        with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=pool)):
            engine = Engine(host="127.0.0.1", port=3306)
            await engine.connect()
            assert engine.is_connected
            await engine.disconnect()
            pool.close.assert_called_once()
            pool.wait_closed.assert_awaited_once()
            assert not engine.is_connected

    async def test_disconnect_idempotent(self):
        """多次 disconnect() 幂等"""
        from autopytest.v2.conftest import make_mock_pool

        pool = make_mock_pool()
        with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=pool)):
            engine = Engine(host="127.0.0.1", port=3306)
            await engine.connect()
            await engine.disconnect()
            await engine.disconnect()  # 不报错
            pool.close.assert_called_once()  # 只关闭一次

    async def test_disconnect_before_connect(self):
        """未连接时 disconnect() 安全"""
        engine = Engine(host="127.0.0.1", port=3306)
        await engine.disconnect()  # 不应抛出

    async def test_await_connect(self):
        """await engine 简写连接"""
        from autopytest.v2.conftest import make_mock_pool

        pool = make_mock_pool()
        with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=pool)):
            engine = Engine(host="127.0.0.1", port=3306)
            result = await engine
            assert result is engine
            assert engine.is_connected

    async def test_async_with_connect(self):
        """async with Engine() as eng 自动连接/断开"""
        from autopytest.v2.conftest import make_mock_pool

        pool = make_mock_pool()
        with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=pool)):
            async with Engine(host="127.0.0.1", port=3306) as eng:
                assert eng.is_connected
            pool.close.assert_called_once()

    async def test_call_connect(self):
        """await engine() 简写连接"""
        from autopytest.v2.conftest import make_mock_pool

        pool = make_mock_pool()
        with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=pool)):
            engine = Engine(host="127.0.0.1", port=3306)
            result = await engine()
            assert result is engine
            assert engine.is_connected

    async def test_connect_race_condition(self):
        """并发 connect() 只创建一个池"""
        from autopytest.v2.conftest import make_mock_pool

        pool = make_mock_pool()
        create_count = 0

        async def mock_create(**kw):
            nonlocal create_count
            create_count += 1
            await asyncio.sleep(0)
            return pool

        with patch("asmysql.v2._engine.create_pool", new=mock_create):
            engine = Engine(host="127.0.0.1", port=3306)
            await asyncio.gather(
                engine.connect(),
                engine.connect(),
                engine.connect(),
            )
            assert create_count == 1
            assert engine.is_connected


# ── TestEngineProperties：属性 ──────────────────────────────────────────


class TestEngineProperties:
    """Engine 属性测试"""

    def test_is_connected_before_connect(self):
        """未连接时 is_connected 为 False"""
        engine = Engine(host="127.0.0.1", port=3306)
        assert engine.is_connected is False

    async def test_is_connected_after_connect(self):
        """连接后 is_connected 为 True"""
        from autopytest.v2.conftest import make_mock_pool

        pool = make_mock_pool()
        with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=pool)):
            engine = Engine(host="127.0.0.1", port=3306)
            await engine.connect()
            assert engine.is_connected is True

    def test_status_disconnected(self):
        """未连接时 status 字段"""
        engine = Engine(host="127.0.0.1", port=3306)
        status = engine.status
        assert status["connected"] is False
        assert status["pool_minsize"] is None
        assert status["pool_maxsize"] is None
        assert status["pool_size"] is None
        assert status["pool_free"] is None
        assert status["pool_used"] is None
        assert "mysql://" in status["address"]

    async def test_status_connected(self):
        """已连接时 status 字段反映真实池信息"""
        from autopytest.v2.conftest import make_mock_pool

        pool = make_mock_pool()
        pool.minsize = 1
        pool.maxsize = 10
        pool.size = 5
        pool.freesize = 3
        with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=pool)):
            engine = Engine(host="127.0.0.1", port=3306)
            await engine.connect()
            status = engine.status
            assert status["connected"] is True
            assert status["pool_minsize"] == 1
            assert status["pool_maxsize"] == 10
            assert status["pool_size"] == 5
            assert status["pool_free"] == 3
            assert status["pool_used"] == 2

    def test_pool_before_connect_raises(self):
        """未连接时访问 pool 属性抛 ConnectionError"""
        engine = Engine(host="127.0.0.1", port=3306)
        with pytest.raises(ConnectionError, match="connect"):
            _ = engine.pool

    async def test_pool_after_connect(self):
        """连接后 pool 属性返回池对象"""
        from autopytest.v2.conftest import make_mock_pool

        pool = make_mock_pool()
        with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=pool)):
            engine = Engine(host="127.0.0.1", port=3306)
            await engine.connect()
            assert engine.pool is pool

    def test_repr_str(self):
        """__repr__ / __str__ 输出"""
        engine = Engine(host="localhost", port=3306, user="root")
        r = repr(engine)
        s = str(engine)
        assert "Engine" in r
        assert "mysql://root@localhost:3306/" in r
        assert "Engine" in s
        assert "mysql://root@localhost:3306/" in s

    def test_url_property(self):
        """url 属性格式 mysql://user@host:port/"""
        engine = Engine(host="localhost", port=3306, user="root")
        assert engine.url == "mysql://root@localhost:3306/"


# ── TestEngineExecute：execute / execute_many ──────────────────────────


class TestEngineExecute:
    """Engine.execute() / execute_many() 返回 Result"""

    async def test_execute_returns_result(self):
        """execute() 返回 Result 实例"""
        from autopytest.v2.conftest import make_mock_pool

        pool = make_mock_pool()
        with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=pool)):
            engine = Engine(host="127.0.0.1", port=3306)
            await engine.connect()
            result = engine.execute("SELECT 1")
            assert isinstance(result, Result)

    async def test_execute_with_params(self):
        """execute() 带参数"""
        from autopytest.v2.conftest import make_mock_pool

        pool = make_mock_pool()
        with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=pool)):
            engine = Engine(host="127.0.0.1", port=3306)
            await engine.connect()
            result = engine.execute("SELECT %s", (1,))
            assert isinstance(result, Result)
            assert result.values == (1,)

    async def test_execute_with_stream(self):
        """execute() stream 模式"""
        from autopytest.v2.conftest import make_mock_pool

        pool = make_mock_pool()
        with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=pool)):
            engine = Engine(host="127.0.0.1", port=3306)
            await engine.connect()
            result = engine.execute("SELECT 1", stream=True)
            assert result.stream is True

    async def test_execute_with_result_class(self):
        """execute() 自定义 result_class"""
        from autopytest.v2.conftest import make_mock_pool

        pool = make_mock_pool()
        with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=pool)):
            engine = Engine(host="127.0.0.1", port=3306)
            await engine.connect()
            result = engine.execute("SELECT 1", result_class=dict)
            assert result._result_class is dict

    def test_execute_before_connect_raises(self):
        """未连接时 execute() 抛 ConnectionError"""
        engine = Engine(host="127.0.0.1", port=3306)
        with pytest.raises(ConnectionError):
            engine.execute("SELECT 1")

    async def test_execute_many_returns_result(self):
        """execute_many() 返回 Result 实例"""
        from autopytest.v2.conftest import make_mock_pool

        pool = make_mock_pool()
        with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=pool)):
            engine = Engine(host="127.0.0.1", port=3306)
            await engine.connect()
            result = engine.execute_many("INSERT INTO t VALUES (%s)", [(1,), (2,)])
            assert isinstance(result, Result)

    async def test_execute_many_with_params(self):
        """execute_many() 带参数"""
        from autopytest.v2.conftest import make_mock_pool

        pool = make_mock_pool()
        with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=pool)):
            engine = Engine(host="127.0.0.1", port=3306)
            await engine.connect()
            data = [("a", 1), ("b", 2)]
            result = engine.execute_many("INSERT INTO t VALUES (%s, %s)", data)
            assert result.values == data


# ── TestEngineMisc：其他方法 ───────────────────────────────────────────


class TestEngineMisc:
    """release_connections 等其他方法"""

    async def test_release_connections(self):
        """release_connections() 调用 pool.clear()"""
        from autopytest.v2.conftest import make_mock_pool

        pool = make_mock_pool()
        with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=pool)):
            engine = Engine(host="127.0.0.1", port=3306)
            await engine.connect()
            await engine.release_connections()
            pool.clear.assert_awaited_once()

    async def test_release_connections_no_pool(self):
        """未连接时 release_connections() 安全"""
        engine = Engine(host="127.0.0.1", port=3306)
        await engine.release_connections()  # 不应抛出
