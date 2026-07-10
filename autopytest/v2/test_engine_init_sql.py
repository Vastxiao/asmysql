#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Engine.init_sql 连接级初始化 SQL 功能测试

验证场景：
1. init_sql 默认值为 None（向后兼容）
2. init_sql 可通过构造参数设置
3. init_sql 可通过 URL query 参数解析
4. connect() 创建池后自动包装 pool.acquire()
5. 新连接首次 acquire 时自动执行 init_sql
6. 同一连接后续 acquire 不重复执行（WeakSet 追踪）
7. 多条连接各自独立初始化
8. init_sql 执行失败时异常向上抛出
9. 不传 init_sql 时 connect() 不包装 acquire（向后兼容）
"""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from asmysql.v2 import Engine

# ── 同步测试：构造参数与 URL 解析 ─────────────────────────────────


def test_init_sql_default_is_none():
    """init_sql 默认值应为 None，保证向后兼容"""
    engine = Engine(host="127.0.0.1", port=3306)
    assert engine.init_sql is None


def test_init_sql_set_via_kwarg():
    """init_sql 可通过关键字参数设置"""
    sql = "SET async_insert = 1, max_execution_time = 30"
    engine = Engine(host="127.0.0.1", port=3306, init_sql=sql)
    assert engine.init_sql == sql


def test_init_sql_parsed_from_url():
    """init_sql 可通过 URL query 参数解析"""
    sql = "SET max_block_size = 12345"
    url = f"mysql://user:pass@127.0.0.1:9004/?init_sql={sql}"
    engine = Engine(url=url)
    assert engine.init_sql == sql


def test_init_sql_kwarg_overrides_class_default():
    """关键字参数 init_sql 覆盖类属性默认值"""
    engine = Engine(init_sql="SET foo = 1")
    assert engine.init_sql == "SET foo = 1"


def test_init_sql_none_kwarg_keeps_default():
    """传入 init_sql=None 时保持类属性默认值（None）"""
    engine = Engine(init_sql=None)
    assert engine.init_sql is None


# ── 异步测试：connect() 与 _apply_pool_init_hook ─────────────────


def _make_mock_pool():
    """创建模拟的 aiomysql Pool，带 acquire/release 方法"""
    pool = MagicMock()
    pool.closed = False
    pool.acquire = AsyncMock()
    pool.release = Mock()
    pool.close = Mock()
    pool.wait_closed = AsyncMock()
    pool.clear = AsyncMock()
    pool.minsize = 1
    pool.maxsize = 2
    pool.size = 1
    pool.freesize = 1
    return pool


def _make_mock_conn():
    """创建模拟的 aiomysql Connection"""
    conn = MagicMock()
    cursor = AsyncMock()
    cursor.execute = AsyncMock()
    cursor.close = AsyncMock()
    conn.cursor = AsyncMock(return_value=cursor)
    return conn, cursor


@pytest.fixture
def mock_pool():
    return _make_mock_pool()


async def test_connect_without_init_sql_does_not_wrap_acquire(mock_pool):
    """不传 init_sql 时，connect() 不包装 pool.acquire"""
    original_acquire = mock_pool.acquire

    with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=mock_pool)):
        engine = Engine(host="127.0.0.1", port=3306)
        await engine.connect()

    # acquire 仍然是原始方法，未被替换
    assert engine.pool.acquire is original_acquire


async def test_connect_with_init_sql_wraps_acquire(mock_pool):
    """传入 init_sql 时，connect() 包装 pool.acquire"""
    original_acquire = mock_pool.acquire

    with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=mock_pool)):
        engine = Engine(host="127.0.0.1", port=3306, init_sql="SET foo = 1")
        await engine.connect()

    # acquire 已被替换为 _acquire_with_init
    assert engine.pool.acquire is not original_acquire


async def test_new_connection_gets_init_sql_on_first_acquire(mock_pool):
    """新连接首次 acquire 时自动执行 init_sql"""
    conn, cursor = _make_mock_conn()
    mock_pool.acquire = AsyncMock(return_value=conn)

    init_sql = "SET async_insert = 1, max_execution_time = 30"

    with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=mock_pool)):
        engine = Engine(host="127.0.0.1", port=3306, init_sql=init_sql)
        await engine.connect()

    # 通过包装后的 acquire 获取连接
    acquired_conn = await engine.pool.acquire()

    # 验证: 创建了 cursor 并执行了 init_sql
    conn.cursor.assert_awaited_once()
    cursor.execute.assert_awaited_once_with(init_sql)
    cursor.close.assert_awaited_once()
    assert acquired_conn is conn


async def test_same_connection_skips_init_sql_on_subsequent_acquire(mock_pool):
    """同一连接后续 acquire 不重复执行 init_sql（WeakSet 追踪）"""
    conn, cursor = _make_mock_conn()
    mock_pool.acquire = AsyncMock(return_value=conn)

    init_sql = "SET foo = 1"

    with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=mock_pool)):
        engine = Engine(host="127.0.0.1", port=3306, init_sql=init_sql)
        await engine.connect()

    # 第一次 acquire：执行 init_sql
    await engine.pool.acquire()
    assert cursor.execute.await_count == 1

    # 第二次 acquire 同一连接：不重复执行
    await engine.pool.acquire()
    assert cursor.execute.await_count == 1

    # 第三次 acquire：仍然不重复
    await engine.pool.acquire()
    assert cursor.execute.await_count == 1


async def test_multiple_connections_each_initialized_once(mock_pool):
    """多条连接各自独立初始化一次"""
    conn1, cursor1 = _make_mock_conn()
    conn2, cursor2 = _make_mock_conn()

    # 模拟 acquire 交替返回不同连接
    acquire_sequence = [conn1, conn2, conn1, conn2]
    mock_pool.acquire = AsyncMock(side_effect=acquire_sequence)

    init_sql = "SET bar = 2"

    with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=mock_pool)):
        engine = Engine(host="127.0.0.1", port=3306, init_sql=init_sql)
        await engine.connect()

    # conn1 首次 acquire → 初始化
    await engine.pool.acquire()
    assert cursor1.execute.await_count == 1

    # conn2 首次 acquire → 初始化
    await engine.pool.acquire()
    assert cursor2.execute.await_count == 1

    # conn1 再次 acquire → 跳过
    await engine.pool.acquire()
    assert cursor1.execute.await_count == 1

    # conn2 再次 acquire → 跳过
    await engine.pool.acquire()
    assert cursor2.execute.await_count == 1


async def test_init_sql_error_propagates(mock_pool):
    """init_sql 执行失败时异常向上抛出"""
    from pymysql.err import OperationalError

    conn, cursor = _make_mock_conn()
    cursor.execute = AsyncMock(side_effect=OperationalError(1064, "Syntax error"))
    mock_pool.acquire = AsyncMock(return_value=conn)

    with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=mock_pool)):
        engine = Engine(host="127.0.0.1", port=3306, init_sql="INVALID SQL")
        await engine.connect()

    with pytest.raises(OperationalError, match="Syntax error"):
        await engine.pool.acquire()

    # cursor 应已关闭（finally 块执行）
    cursor.close.assert_awaited_once()


async def test_weakset_allows_reinit_after_connection_gc(mock_pool):
    """
    当连接被 GC 回收后（模拟 pool_recycle 场景），
    WeakSet 自动清理，新连接对象会重新执行 init_sql。
    """
    import gc

    conn1, cursor1 = _make_mock_conn()
    conn2, cursor2 = _make_mock_conn()

    # 使用 side_effect 列表，让 original_acquire 依次返回 conn1 → conn2
    mock_pool.acquire = AsyncMock(side_effect=[conn1, conn2])

    init_sql = "SET foo = 1"

    with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=mock_pool)):
        engine = Engine(host="127.0.0.1", port=3306, init_sql=init_sql)
        await engine.connect()

    # conn1 首次 acquire → 初始化
    await engine.pool.acquire()
    assert cursor1.execute.await_count == 1

    # 模拟连接被回收：删除 conn1 引用，强制 GC
    del conn1
    del cursor1
    gc.collect()

    # conn2 是全新的 Connection 对象（不在 WeakSet 中），应重新初始化
    await engine.pool.acquire()
    assert cursor2.execute.await_count == 1


async def test_disconnect_clears_pool(mock_pool):
    """disconnect() 正常关闭池并置空"""
    with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=mock_pool)):
        engine = Engine(host="127.0.0.1", port=3306, init_sql="SET foo = 1")
        await engine.connect()
        assert engine.is_connected

        await engine.disconnect()
        mock_pool.close.assert_called_once()
        mock_pool.wait_closed.assert_awaited_once()
        assert not engine.is_connected


async def test_connect_idempotent(mock_pool):
    """多次调用 connect() 不会重复创建池或重复包装"""
    original_acquire = mock_pool.acquire  # noqa: F841

    with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=mock_pool)) as mock_create:
        engine = Engine(host="127.0.0.1", port=3306, init_sql="SET foo = 1")
        await engine.connect()
        wrapped_acquire = engine.pool.acquire

        # 再次调用 connect()
        await engine.connect()
        # create_pool 只被调用一次
        mock_create.assert_awaited_once()
        # acquire 包装不会叠加（因为 __pool 已存在，if not self.__pool 守卫生效）
        assert engine.pool.acquire is wrapped_acquire


async def test_init_sql_with_url_integration(mock_pool):
    """通过 URL 传入 init_sql 的端到端测试"""
    conn, cursor = _make_mock_conn()
    mock_pool.acquire = AsyncMock(return_value=conn)

    init_sql = "SET max_block_size = 99"
    url = f"mysql://user:pass@127.0.0.1:9004/?init_sql={init_sql}"

    with patch("asmysql.v2._engine.create_pool", new=AsyncMock(return_value=mock_pool)):
        engine = Engine(url=url)
        assert engine.init_sql == init_sql
        await engine.connect()

    await engine.pool.acquire()
    cursor.execute.assert_awaited_once_with(init_sql)
