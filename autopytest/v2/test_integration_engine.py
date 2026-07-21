#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Engine 属性与连接池集成测试

使用真实 MySQL 验证 Engine 的所有公开 API：
连接/断开、上下文管理器、属性（status/is_connected/pool/url/repr/str）、
release_connections。
"""

from urllib.parse import quote

import pytest

from asmysql.v2 import Engine

pytestmark = pytest.mark.integration

_TEST_DB = "asmysql_test_engine"


@pytest.fixture
async def engine(mysql_url):
    """创建并连接 Engine，测试结束后断开连接。

    通过 init_sql 在每条连接上自动执行 USE 选择测试数据库。
    """
    # 1. 创建测试数据库
    setup_eng = Engine(mysql_url)
    try:
        await setup_eng.connect()
    except ConnectionError:
        pytest.skip("MySQL 数据库不可用，跳过集成测试")
    async with setup_eng.execute(f"CREATE DATABASE IF NOT EXISTS `{_TEST_DB}`"):
        pass
    await setup_eng.disconnect()

    # 2. 创建带 init_sql 的 Engine
    eng = Engine(mysql_url + "?init_sql=" + quote(f"USE `{_TEST_DB}`"))
    await eng.connect()
    yield eng
    await eng.disconnect()

    # 3. 清理测试数据库
    cleanup_eng = Engine(mysql_url)
    await cleanup_eng.connect()
    async with cleanup_eng.execute(f"DROP DATABASE IF EXISTS `{_TEST_DB}`"):
        pass
    await cleanup_eng.disconnect()


# ── TestEngineConnection：连接生命周期 ──────────────────────────────────


class TestEngineConnection:
    """Engine 连接/断开生命周期"""

    async def test_connect_and_disconnect(self, mysql_url):
        """connect/disconnect 完整生命周期"""
        eng = Engine(mysql_url)
        try:
            await eng.connect()
        except ConnectionError:
            pytest.skip("MySQL 不可用")
        assert eng.is_connected
        await eng.disconnect()
        assert not eng.is_connected

    async def test_connect_idempotent(self, mysql_url):
        """多次 connect 幂等"""
        eng = Engine(mysql_url)
        try:
            await eng.connect()
        except ConnectionError:
            pytest.skip("MySQL 不可用")
        await eng.connect()
        await eng.connect()
        assert eng.is_connected
        await eng.disconnect()

    async def test_disconnect_idempotent(self, mysql_url):
        """多次 disconnect 幂等"""
        eng = Engine(mysql_url)
        try:
            await eng.connect()
        except ConnectionError:
            pytest.skip("MySQL 不可用")
        await eng.disconnect()
        await eng.disconnect()
        assert not eng.is_connected

    async def test_async_with_context_manager(self, mysql_url):
        """async with Engine(url) as eng 自动连接/断开"""
        try:
            async with Engine(mysql_url) as eng:
                assert eng.is_connected
        except ConnectionError:
            pytest.skip("MySQL 不可用")
        assert not eng.is_connected

    async def test_await_shorthand(self, mysql_url):
        """eng = await Engine(url) 简写连接"""
        eng = Engine(mysql_url)
        try:
            result = await eng
        except ConnectionError:
            pytest.skip("MySQL 不可用")
        assert result is eng
        assert eng.is_connected
        await eng.disconnect()

    async def test_call_shorthand(self, mysql_url):
        """eng = await Engine(url)() 简写连接"""
        eng = Engine(mysql_url)
        try:
            result = await eng()
        except ConnectionError:
            pytest.skip("MySQL 不可用")
        assert result is eng
        assert eng.is_connected
        await eng.disconnect()

    async def test_connect_error_invalid_host(self):
        """连接无效主机抛 ConnectionError"""
        eng = Engine(host="192.0.2.1", port=3306, connect_timeout=1)
        with pytest.raises(ConnectionError):
            await eng.connect()


# ── TestEngineProperties：属性 ──────────────────────────────────────────


class TestEngineProperties:
    """Engine 属性测试（真实 MySQL）"""

    def test_is_connected_before_connect(self, mysql_url):
        """未连接时 is_connected 为 False"""
        eng = Engine(mysql_url)
        assert eng.is_connected is False

    async def test_is_connected_lifecycle(self, engine):
        """连接后 is_connected 为 True"""
        assert engine.is_connected is True

    async def test_status_disconnected(self, mysql_url):
        """未连接时 status 字段"""
        eng = Engine(mysql_url)
        status = eng.status
        assert status["connected"] is False
        assert status["pool_minsize"] is None
        assert status["pool_maxsize"] is None
        assert status["pool_size"] is None
        assert status["pool_free"] is None
        assert status["pool_used"] is None

    async def test_status_connected(self, engine):
        """已连接时 status 字段反映真实池信息"""
        status = engine.status
        assert status["connected"] is True
        assert status["pool_minsize"] is not None
        assert status["pool_maxsize"] is not None
        assert status["pool_size"] is not None
        assert status["pool_free"] is not None
        assert status["pool_used"] is not None
        assert status["pool_minsize"] >= 1
        assert status["pool_maxsize"] >= status["pool_minsize"]
        assert status["pool_size"] >= 0
        assert status["pool_free"] >= 0
        assert status["pool_used"] >= 0

    async def test_url_property_format(self, engine):
        """url 属性格式 mysql://user@host:port/"""
        url = engine.url
        assert url.startswith("mysql://")
        assert "@" in url
        assert ":" in url

    async def test_repr_str(self, engine):
        """__repr__ / __str__ 输出"""
        r = repr(engine)
        s = str(engine)
        assert "Engine" in r
        assert "mysql://" in r
        assert "Engine" in s
        assert "mysql://" in s

    async def test_pool_property(self, engine):
        """pool 属性返回真实 aiomysql.Pool"""
        pool = engine.pool
        assert pool is not None
        assert hasattr(pool, "acquire")
        assert hasattr(pool, "release")

    async def test_pool_before_connect_raises(self, mysql_url):
        """未连接时访问 pool 抛 ConnectionError"""
        eng = Engine(mysql_url)
        with pytest.raises(ConnectionError):
            _ = eng.pool


# ── TestEngineReleaseConnections：release_connections ───────────────────


class TestEngineReleaseConnections:
    """release_connections 集成测试"""

    async def test_release_connections(self, engine):
        """release_connections() 后空闲连接被清理"""
        # 先执行一个查询建立连接
        async with engine.execute("SELECT 1"):
            pass
        await engine.release_connections()
        # 不报错即通过

    async def test_release_connections_no_error(self, mysql_url):
        """未连接时调用 release_connections() 安全"""
        eng = Engine(mysql_url)
        await eng.release_connections()  # 不应抛出
