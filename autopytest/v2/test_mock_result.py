# -*- coding: utf-8 -*-

"""
Result 类全量 Mock 测试

覆盖 Result 所有公开 API：属性、execute（__call__）、fetch 方法、
上下文管理器（async with / async for / iterate）、close、_should_commit、__del__。
全部使用 Mock，无需真实 MySQL 数据库。
"""

import warnings
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel
from pymysql.err import MySQLError

from asmysql.v2._error import err_msg
from autopytest.v2.conftest import make_mock_conn, make_mock_pool, make_result


class CustomModel(BaseModel):
    id: int
    name: str


# ── TestResultProperties：属性 ──────────────────────────────────────────


class TestResultProperties:
    """Result 属性测试"""

    def test_error_default_none(self):
        """error 默认为 None"""
        result = make_result()
        assert result.error is None

    def test_error_no_without_error(self):
        """无错误时 error_no 返回 0"""
        result = make_result()
        assert result.error_no == 0

    def test_error_no_with_error(self):
        """有错误时 error_no 返回错误码"""
        result = make_result()
        result._Result__error = MySQLError(1045, "Access denied")
        assert result.error_no == 1045

    def test_error_msg_without_error(self):
        """无错误时 error_msg 返回空字符串"""
        result = make_result()
        assert result.error_msg == ""

    def test_error_msg_with_error(self):
        """有错误时 error_msg 包含格式化信息"""
        result = make_result()
        err = MySQLError(1045, "Access denied")
        result._Result__error = err
        expected = err_msg(err)
        assert result.error_msg == expected
        assert "Access denied" in result.error_msg

    async def test_row_count_with_data(self):
        """execute 后 row_count 返回受影响行数"""
        conn, cursor = make_mock_conn()
        cursor.rowcount = 42
        cursor.description = None  # DDL/DML 无结果集
        pool = make_mock_pool(conn)
        result = make_result(pool=pool)
        async with result as r:
            assert r.row_count == 42

    async def test_row_count_stream_returns_none(self):
        """stream 模式 row_count 返回 None"""
        conn, cursor = make_mock_conn()
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        result = make_result(pool=pool, stream=True)
        async with result as r:
            assert r.row_count is None

    async def test_row_count_after_close_cached(self):
        """DDL/DML close 后 row_count 使用缓存值"""
        conn, cursor = make_mock_conn()
        cursor.rowcount = 5
        cursor.description = None  # DDL 无结果集，自动释放
        pool = make_mock_pool(conn)
        result = make_result(pool=pool, query="INSERT INTO t VALUES (1)")
        await result.__call__()
        # 游标已关闭，使用缓存
        assert result.row_count == 5

    async def test_last_rowid_after_insert(self):
        """INSERT 后 last_rowid 返回自增 ID"""
        conn, cursor = make_mock_conn()
        cursor.lastrowid = 99
        cursor.description = None
        pool = make_mock_pool(conn)
        result = make_result(pool=pool, query="INSERT INTO t VALUES (1)")
        async with result as r:
            assert r.last_rowid == 99

    async def test_last_rowid_after_close_cached(self):
        """close 后 last_rowid 使用缓存值"""
        conn, cursor = make_mock_conn()
        cursor.lastrowid = 99
        cursor.description = None
        pool = make_mock_pool(conn)
        result = make_result(pool=pool, query="INSERT INTO t VALUES (1)")
        await result.__call__()
        assert result.last_rowid == 99

    async def test_row_number_property(self):
        """row_number 返回当前游标位置"""
        conn, cursor = make_mock_conn()
        cursor.rownumber = 5
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        result = make_result(pool=pool)
        async with result as r:
            assert r.row_number == 5

    async def test_row_number_after_close(self):
        """close 后 row_number 返回 None"""
        conn, cursor = make_mock_conn()
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        result = make_result(pool=pool)
        async with result as r:
            pass
        assert r.row_number is None

    def test_repr(self):
        """__repr__ 包含查询语句"""
        result = make_result(query="SELECT * FROM users")
        assert "Result" in repr(result)
        assert "SELECT * FROM users" in repr(result)


# ── TestResultExecute：__call__ 执行逻辑 ───────────────────────────────


class TestResultExecute:
    """Result.__call__() 执行逻辑"""

    async def test_call_executes_sql(self):
        """__call__ 执行 SQL"""
        conn, cursor = make_mock_conn()
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        result = make_result(pool=pool, query="SELECT 1")
        await result.__call__()
        cursor.execute.assert_awaited_once_with("SELECT 1", None)

    async def test_call_idempotent(self):
        """__call__ 幂等，多次调用只执行一次"""
        conn, cursor = make_mock_conn()
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        result = make_result(pool=pool)
        await result.__call__()
        await result.__call__()
        assert cursor.execute.await_count == 1

    async def test_call_mysql_error_stored(self):
        """MySQLError 存储在 result.error"""
        conn, cursor = make_mock_conn()
        cursor.execute = AsyncMock(side_effect=MySQLError(1064, "Syntax error"))
        pool = make_mock_pool(conn)
        result = make_result(pool=pool)
        async with result as r:
            assert r.error is not None
            assert r.error_no == 1064

    async def test_call_non_mysql_error_reraises(self):
        """非 MySQLError 异常重新抛出"""
        conn = MagicMock()
        conn.cursor = AsyncMock(side_effect=OSError("Connection reset"))
        pool = make_mock_pool(conn)
        result = make_result(pool=pool)
        with pytest.raises(OSError, match="Connection reset"):
            async with result:
                pass

    async def test_call_auto_commit_write_sql(self):
        """写操作 SQL 自动 commit"""
        conn, cursor = make_mock_conn()
        cursor.description = None
        pool = make_mock_pool(conn)
        result = make_result(pool=pool, query="INSERT INTO t VALUES (1)")
        async with result:
            pass
        conn.commit.assert_awaited_once()

    async def test_call_no_commit_read_sql(self):
        """读操作 SQL 不 commit"""
        conn, cursor = make_mock_conn()
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        result = make_result(pool=pool, query="SELECT 1")
        async with result:
            pass
        conn.commit.assert_not_awaited()

    async def test_call_no_commit_stream_mode(self):
        """stream 模式不 commit"""
        conn, cursor = make_mock_conn()
        pool = make_mock_pool(conn)
        result = make_result(pool=pool, query="INSERT INTO t VALUES (1)", stream=True)
        async with result:
            pass
        conn.commit.assert_not_awaited()

    async def test_call_ddl_auto_releases_connection(self):
        """DDL/DML（无结果集）自动释放连接"""
        conn, cursor = make_mock_conn()
        cursor.description = None
        cursor.rowcount = 0
        pool = make_mock_pool(conn)
        result = make_result(pool=pool, query="CREATE TABLE t (id INT)")
        await result.__call__()
        pool.release.assert_called_with(conn)


# ── TestResultFetch：fetch 方法 ─────────────────────────────────────────


class TestResultFetch:
    """Result.fetch_one / fetch_many / fetch_all"""

    async def test_fetch_one_tuple(self):
        """fetch_one 返回 tuple"""
        conn, cursor = make_mock_conn()
        cursor.fetchone = AsyncMock(return_value=(1, "Alice"))
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        async with make_result(pool=pool) as r:
            data = await r.fetch_one()
            assert data == (1, "Alice")

    async def test_fetch_one_dict(self):
        """fetch_one 返回 dict"""
        conn, cursor = make_mock_conn()
        cursor.fetchone = AsyncMock(return_value={"id": 1, "name": "Alice"})
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        async with make_result(pool=pool, result_class=dict) as r:
            data = await r.fetch_one()
            assert data == {"id": 1, "name": "Alice"}

    async def test_fetch_one_custom_class(self):
        """fetch_one 返回自定义 Pydantic Model"""
        conn, cursor = make_mock_conn()
        cursor.fetchone = AsyncMock(return_value={"id": 1, "name": "Alice"})
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        async with make_result(pool=pool, result_class=CustomModel) as r:
            data = await r.fetch_one()
            assert isinstance(data, CustomModel)
            assert data.name == "Alice"

    async def test_fetch_one_returns_none_on_exhaustion(self):
        """fetch_one 数据耗尽返回 None"""
        conn, cursor = make_mock_conn()
        cursor.fetchone = AsyncMock(return_value=None)
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        async with make_result(pool=pool) as r:
            data = await r.fetch_one()
            assert data is None

    async def test_fetch_one_returns_none_on_error(self):
        """有错误时 fetch_one 返回 None"""
        conn, cursor = make_mock_conn()
        cursor.execute = AsyncMock(side_effect=MySQLError(1064, "err"))
        pool = make_mock_pool(conn)
        async with make_result(pool=pool) as r:
            assert r.error is not None
            data = await r.fetch_one()
            assert data is None

    async def test_fetch_many_tuple(self):
        """fetch_many 返回 tuple 列表"""
        conn, cursor = make_mock_conn()
        cursor.fetchmany = AsyncMock(return_value=[(1, "a"), (2, "b")])
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        async with make_result(pool=pool) as r:
            data = await r.fetch_many(2)
            assert data == [(1, "a"), (2, "b")]

    async def test_fetch_many_dict(self):
        """fetch_many 返回 dict 列表"""
        conn, cursor = make_mock_conn()
        cursor.fetchmany = AsyncMock(return_value=[{"id": 1}, {"id": 2}])
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        async with make_result(pool=pool, result_class=dict) as r:
            data = await r.fetch_many(2)
            assert data == [{"id": 1}, {"id": 2}]

    async def test_fetch_many_custom_class(self):
        """fetch_many 返回自定义 Model 列表"""
        conn, cursor = make_mock_conn()
        cursor.fetchmany = AsyncMock(
            return_value=[{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
        )
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        async with make_result(pool=pool, result_class=CustomModel) as r:
            data = await r.fetch_many(2)
            assert len(data) == 2
            assert all(isinstance(d, CustomModel) for d in data)

    async def test_fetch_many_with_size(self):
        """fetch_many(size=N) 传递 size 参数"""
        conn, cursor = make_mock_conn()
        cursor.fetchmany = AsyncMock(return_value=[(1,)])
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        async with make_result(pool=pool) as r:
            await r.fetch_many(5)
            cursor.fetchmany.assert_awaited_once_with(5)

    async def test_fetch_many_empty_result(self):
        """fetch_many 空结果返回空列表"""
        conn, cursor = make_mock_conn()
        cursor.fetchmany = AsyncMock(return_value=[])
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        async with make_result(pool=pool) as r:
            data = await r.fetch_many(10)
            assert data == []

    async def test_fetch_all_tuple(self):
        """fetch_all 返回 tuple 列表"""
        conn, cursor = make_mock_conn()
        cursor.fetchall = AsyncMock(return_value=[(1, "a"), (2, "b")])
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        async with make_result(pool=pool) as r:
            data = await r.fetch_all()
            assert data == [(1, "a"), (2, "b")]

    async def test_fetch_all_dict(self):
        """fetch_all 返回 dict 列表"""
        conn, cursor = make_mock_conn()
        cursor.fetchall = AsyncMock(return_value=[{"id": 1}, {"id": 2}])
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        async with make_result(pool=pool, result_class=dict) as r:
            data = await r.fetch_all()
            assert data == [{"id": 1}, {"id": 2}]

    async def test_fetch_all_custom_class(self):
        """fetch_all 返回自定义 Model 列表"""
        conn, cursor = make_mock_conn()
        cursor.fetchall = AsyncMock(
            return_value=[{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
        )
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        async with make_result(pool=pool, result_class=CustomModel) as r:
            data = await r.fetch_all()
            assert len(data) == 2
            assert all(isinstance(d, CustomModel) for d in data)

    async def test_fetch_all_auto_closes(self):
        """fetch_all 自动关闭连接"""
        conn, cursor = make_mock_conn()
        cursor.fetchall = AsyncMock(return_value=[(1,)])
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        result = make_result(pool=pool)
        async with result as r:
            await r.fetch_all()
        pool.release.assert_called_with(conn)


# ── TestResultContextManager：上下文管理器 ───────────────────────────────


class TestResultContextManager:
    """async with / async for / iterate() 上下文管理"""

    async def test_async_with_enter_exit(self):
        """async with 正常进入/退出"""
        conn, cursor = make_mock_conn()
        pool = make_mock_pool(conn)
        result = make_result(pool=pool)
        async with result as r:
            assert r is result
        pool.release.assert_called_with(conn)

    async def test_async_with_on_error(self):
        """async with 内部出错仍释放连接"""
        conn, cursor = make_mock_conn()
        cursor.execute = AsyncMock(side_effect=MySQLError(1064, "err"))
        pool = make_mock_pool(conn)
        async with make_result(pool=pool) as r:
            assert r.error is not None
        pool.release.assert_called_with(conn)

    async def test_async_for_iteration(self):
        """async for 完整迭代"""
        conn, cursor = make_mock_conn()
        cursor.description = (("col",),)  # 模拟有结果集
        cursor.fetchone = AsyncMock(side_effect=[(1,), (2,), (3,), None])
        pool = make_mock_pool(conn)
        result = make_result(pool=pool)
        collected = []
        async for item in result:
            collected.append(item)
        assert collected == [(1,), (2,), (3,)]

    async def test_async_for_break_releases(self):
        """async for break 后通过 aclose() 释放连接"""
        conn, cursor = make_mock_conn()
        cursor.description = (("col",),)  # 模拟有结果集
        cursor.fetchone = AsyncMock(side_effect=[(1,), (2,), (3,)])
        pool = make_mock_pool(conn)
        result = make_result(pool=pool)
        it = result.__aiter__()
        count = 0
        try:
            async for item in it:
                count += 1
                break
        finally:
            await it.aclose()
        assert count == 1
        pool.release.assert_called_with(conn)

    async def test_iterate_method(self):
        """iterate() 完整迭代 tuple"""
        conn, cursor = make_mock_conn()
        cursor.description = (("col",),)  # 模拟有结果集
        cursor.fetchone = AsyncMock(side_effect=[(1, "a"), (2, "b"), None])
        pool = make_mock_pool(conn)
        result = make_result(pool=pool)
        async with result as r:
            collected = []
            async for item in r.iterate():
                collected.append(item)
            assert collected == [(1, "a"), (2, "b")]

    async def test_iterate_dict_class(self):
        """iterate() 使用 dict result_class"""
        conn, cursor = make_mock_conn()
        cursor.description = (("col",),)  # 模拟有结果集
        cursor.fetchone = AsyncMock(side_effect=[{"id": 1}, {"id": 2}, None])
        pool = make_mock_pool(conn)
        result = make_result(pool=pool, result_class=dict)
        async with result as r:
            collected = []
            async for item in r.iterate():
                collected.append(item)
            assert collected == [{"id": 1}, {"id": 2}]

    async def test_iterate_custom_class(self):
        """iterate() 使用自定义 result_class"""
        conn, cursor = make_mock_conn()
        cursor.description = (("col",),)  # 模拟有结果集
        cursor.fetchone = AsyncMock(
            side_effect=[{"id": 1, "name": "A"}, {"id": 2, "name": "B"}, None]
        )
        pool = make_mock_pool(conn)
        result = make_result(pool=pool, result_class=CustomModel)
        async with result as r:
            collected = []
            async for item in r.iterate():
                collected.append(item)
            assert len(collected) == 2
            assert all(isinstance(c, CustomModel) for c in collected)


# ── TestResultClose：close 方法 ─────────────────────────────────────────


class TestResultClose:
    """Result.close() 幂等性与安全性"""

    async def test_close_releases_connection(self):
        """close() 释放连接"""
        conn, cursor = make_mock_conn()
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        result = make_result(pool=pool)
        async with result:
            pass
        pool.release.assert_called_with(conn)

    async def test_close_idempotent(self):
        """close() 多次调用安全"""
        conn, cursor = make_mock_conn()
        pool = make_mock_pool(conn)
        result = make_result(pool=pool)
        async with result:
            pass
        await result.close()
        await result.close()
        assert pool.release.call_count == 1

    async def test_close_without_execute_safe(self):
        """未执行 SQL 时 close() 安全"""
        result = make_result()
        await result.close()  # 不应抛出


# ── TestResultShouldCommit：自动 commit 判断 ────────────────────────────


class TestResultShouldCommit:
    """_should_commit() 根据 SQL 首关键词判断"""

    async def test_insert_commits(self):
        """INSERT 触发 commit"""
        conn, cursor = make_mock_conn()
        cursor.description = None
        pool = make_mock_pool(conn)
        async with make_result(pool=pool, query="INSERT INTO t VALUES (1)"):
            pass
        conn.commit.assert_awaited_once()

    async def test_update_commits(self):
        """UPDATE 触发 commit"""
        conn, cursor = make_mock_conn()
        cursor.description = None
        pool = make_mock_pool(conn)
        async with make_result(pool=pool, query="UPDATE t SET a=1"):
            pass
        conn.commit.assert_awaited_once()

    async def test_delete_commits(self):
        """DELETE 触发 commit"""
        conn, cursor = make_mock_conn()
        cursor.description = None
        pool = make_mock_pool(conn)
        async with make_result(pool=pool, query="DELETE FROM t WHERE id=1"):
            pass
        conn.commit.assert_awaited_once()

    async def test_select_no_commit(self):
        """SELECT 不触发 commit"""
        conn, cursor = make_mock_conn()
        cursor.description = (("col",),)
        pool = make_mock_pool(conn)
        async with make_result(pool=pool, query="SELECT 1"):
            pass
        conn.commit.assert_not_awaited()

    async def test_create_commits(self):
        """CREATE 触发 commit"""
        conn, cursor = make_mock_conn()
        cursor.description = None
        pool = make_mock_pool(conn)
        async with make_result(pool=pool, query="CREATE TABLE t (id INT)"):
            pass
        conn.commit.assert_awaited_once()

    async def test_drop_commits(self):
        """DROP 触发 commit"""
        conn, cursor = make_mock_conn()
        cursor.description = None
        pool = make_mock_pool(conn)
        async with make_result(pool=pool, query="DROP TABLE t"):
            pass
        conn.commit.assert_awaited_once()

    async def test_comment_prefix_sql(self):
        """SQL 含前导注释时正确识别关键词"""
        conn, cursor = make_mock_conn()
        cursor.description = None
        pool = make_mock_pool(conn)
        async with make_result(pool=pool, query="/* comment */ INSERT INTO t VALUES (1)"):
            pass
        conn.commit.assert_awaited_once()

    async def test_replace_commits(self):
        """REPLACE 触发 commit"""
        conn, cursor = make_mock_conn()
        cursor.description = None
        pool = make_mock_pool(conn)
        async with make_result(pool=pool, query="REPLACE INTO t VALUES (1)"):
            pass
        conn.commit.assert_awaited_once()

    async def test_truncate_commits(self):
        """TRUNCATE 触发 commit"""
        conn, cursor = make_mock_conn()
        cursor.description = None
        pool = make_mock_pool(conn)
        async with make_result(pool=pool, query="TRUNCATE TABLE t"):
            pass
        conn.commit.assert_awaited_once()

    async def test_alter_commits(self):
        """ALTER 触发 commit"""
        conn, cursor = make_mock_conn()
        cursor.description = None
        pool = make_mock_pool(conn)
        async with make_result(pool=pool, query="ALTER TABLE t ADD COLUMN c INT"):
            pass
        conn.commit.assert_awaited_once()


# ── TestResultDel：__del__ 安全网 ──────────────────────────────────────


class TestResultDel:
    """Result.__del__() GC 安全网"""

    def test_del_warns_unclosed(self):
        """未关闭的 Result 在 GC 时发出 ResourceWarning"""
        conn, cursor = make_mock_conn()
        pool = make_mock_pool(conn)
        result = make_result(pool=pool)
        # 模拟已执行但未关闭
        result._Result__cursor = cursor
        result._Result__executed = True
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result.__del__()
            assert any(issubclass(x.category, ResourceWarning) for x in w)

    def test_del_safe_no_cursor(self):
        """cursor 为 None 时 __del__ 安全"""
        result = make_result()
        result.__del__()  # 不应抛出

    def test_del_safe_no_pool(self):
        """pool 为 None 时 __del__ 安全"""
        result = make_result()
        result.pool = None
        result.__del__()  # 不应抛出
