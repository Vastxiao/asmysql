# -*- coding: utf-8 -*-

"""V2 测试共享 fixtures

提供 Mock 测试和集成测试共用的基础设施。
Mock 测试无需真实 MySQL，集成测试需要可用的 MySQL 数据库。
"""

from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from asmysql.v2 import AsMysql, Engine, Result

# ── Mock 工具函数（可在 fixture 和测试中复用）──────────────────────────


def make_mock_cursor():
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
    cursor.description = None
    return cursor


def make_mock_conn(cursor=None):
    """创建模拟的 aiomysql Connection，绑定 cursor"""
    conn = MagicMock()
    if cursor is None:
        cursor = make_mock_cursor()
    cursor.connection = conn
    conn.cursor = AsyncMock(return_value=cursor)
    conn.commit = AsyncMock()
    conn.rollback = AsyncMock()
    return conn, cursor


def make_mock_pool(conn=None):
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


def make_result(pool=None, **kwargs):
    """创建 Result 实例，提供合理的默认 mock 值"""
    if pool is None:
        pool = make_mock_pool()
    defaults = dict(
        pool=pool,
        query="SELECT 1",
        values=None,
        execute_many=False,
        stream=False,
        result_class=tuple,
    )
    defaults.update(kwargs)
    return Result(**defaults)


# ── Mock Fixtures ──────────────────────────────────────────────────────


@pytest.fixture
def mock_cursor():
    """创建模拟的 aiomysql Cursor"""
    return make_mock_cursor()


@pytest.fixture
def mock_conn(mock_cursor):
    """创建模拟的 aiomysql Connection，绑定 mock_cursor"""
    conn, _ = make_mock_conn(mock_cursor)
    return conn


@pytest.fixture
def mock_pool(mock_conn):
    """创建模拟的 aiomysql Pool，绑定 mock_conn"""
    pool = make_mock_pool(mock_conn)
    return pool


@pytest.fixture
def make_result_factory(mock_pool):
    """Result 实例工厂函数（依赖 mock_pool）"""
    def _factory(**kwargs):
        return make_result(pool=mock_pool, **kwargs)
    return _factory


# ── AsMysql Mock Fixtures（兼容性）────────────────────────────────────


@pytest.fixture
def mock_engine():
    """创建一个 Mock 的 Engine 实例"""
    engine = Mock(spec=Engine)
    engine.url = "mysql://root@localhost:3306/"
    engine.host = "localhost"
    engine.port = 3306
    return engine


@pytest.fixture
def asmysql(mock_engine):
    """创建使用 mock engine 的 AsMysql 实例"""
    return AsMysql(mock_engine)


@pytest.fixture
def mock_result():
    """创建一个 Mock 的 Result 实例"""
    result = Mock(spec=Result)
    result.error = None
    result.row_count = 1
    return result
