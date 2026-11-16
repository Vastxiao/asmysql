# asmysql v2 API 速查

> 本文件是 asmysql-dev skill 的本地参考，内容依据包源码与架构文档核验。
> 使用前必须先完成 SKILL.md 第 1 节的版本自检；版本不匹配时改读包内 skill 或在线来源。

## Engine 配置

类级别默认值 + 构造关键字参数 + URL 查询参数三通道。URL 格式：

```text
mysql://user:pass@host:port/?charset=utf8mb4&param=value
```

scheme 必须为 `mysql`；用户名/密码自动 URL 解码。

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `host` / `port` | `127.0.0.1` / `3306` | 服务地址 |
| `user` / `password` | `""` / `""` | 凭据 |
| `charset` | `utf8mb4` | 字符集 |
| `min_pool_size` / `max_pool_size` | `1` / `10` | 连接池大小 |
| `pool_recycle` | `-1` | 空闲 TCP 连接回收秒数 |
| `connect_timeout` | `5` | 连接超时秒数 |
| `echo_sql_log` | `False` | 打印 SQL 日志（URL 中按 `true/1/yes` 解析） |
| `init_sql` | `None` | 每条新连接首次使用自动执行的 SQL（如 ClickHouse MySQL 协议的会话 SET） |
| `disconnect_timeout` | `None` | disconnect 等待秒数；`None` 无限等待，有限值超时 terminate（URL 中 `none` 解析为 None） |

`autocommit` **不是配置参数**：库内置 `True`，正常语句由服务端自动提交，客户端仅在服务端报告处于事务中时兜底 COMMIT/ROLLBACK。

## 连接生命周期

```python
from asmysql import Engine

engine = Engine("mysql://user:pass@host:3306/")
await engine.connect()
# ... 业务 ...
await engine.disconnect()
```

连接简写（均等价 connect）：

- `async with engine:` —— 进入时 connect，退出时 disconnect；
- `await engine`、`await engine()` —— 仅 connect，需自行 disconnect。

其他生命周期 API：

- `terminate()`：同步、幂等强制清理（关闭全部在用与空闲连接），适用 atexit/同步 shutdown 钩子；清理后可重新 connect。
- `release_connections()`：释放全部空闲连接。
- `is_connected` / `status`（`EngineStatus`：address/connected/pool_minsize/maxsize/size/free/used）/ `pool`（未连接抛 `ConnectionError`）。
- 活池只属于创建它的事件循环；支持「原循环 disconnect → 新循环 connect」复用（如多次 `asyncio.run()`）。

## execute / execute_many

```python
engine.execute(query, values=None, *, stream=None, result_class=tuple)      # -> Result
engine.execute_many(query, values, *, stream=None, result_class=tuple)      # -> Result
```

- 返回**懒执行 `Result` 对象，不是协程**；禁止 `await engine.execute(...)`。
- `values`：序列或 dict（占位符参数化，防注入）；`execute_many` 收参数组序列。
- `stream=True`：流式游标，逐行读取不缓冲全量，大结果集必用。
- `result_class`：行映射类型，见下表。
- `execute_many([])`：不 acquire、不发 SQL，发 `UserWarning`，`row_count=0`。
- 未 connect 时调用 execute 会因访问 `engine.pool` 抛 `ConnectionError`。

## Result 标准用法白名单

仅推荐以下用法（连接生命周期自动管理，数据耗尽或 close 后自动归还连接）：

```python
# 1. async with（推荐默认姿势）
async with engine.execute(sql, args) as result:
    if result.error:
        raise result.error
    rows = await result.fetch_all()

# 2. async for（break 也能正确释放连接）
async for row in engine.execute(sql, stream=True):
    if row[0] == target:
        break

# 3. fetch_all()（finally 自动 close）
async with engine.execute(sql) as result:
    rows = await result.fetch_all()

# 4. iterate() 异步生成器
async with engine.execute(sql) as result:
    if result.error:
        raise result.error
    async for row in result.iterate():
        ...

# 5. 无结果集语句（DDL/DML）：缓存 rowcount/lastrowid 后自动关游标、归还连接
async with engine.execute("UPDATE mydb.t SET x=%s WHERE id=%s", (1, 2)) as result:
    if result.error:
        raise result.error
    print(result.row_count, result.last_rowid)
```

取数 API：`fetch_one()`（无数据返回 None）、`fetch_many(size)`、`fetch_all()`、`iterate()`。
不推荐：裸执行（`await result()`）后 fetch 且不 close（仅由 GC 安全网兜底，连接被丢弃不复用）。

## result_class 游标映射

| result_class | stream=False | stream=True |
|--------------|--------------|-------------|
| `tuple`（默认） | `Cursor` | `SSCursor` |
| `dict` / 自定义类 | `DictCursor` | `SSDictCursor` |

`tuple`/`dict` 直接透传；其他类按 `result_class(**row_dict)` 构造（如 Pydantic `BaseModel`，须支持 `**kwargs`）。

```python
async with engine.execute("SELECT id, name FROM mydb.users", result_class=dict) as result:
    rows = await result.fetch_all()  # list[dict]
```

## AsMysql 业务基类

```python
from asmysql import AsMysql, Engine

class UserRepo(AsMysql):
    async def get_name(self, uid: int) -> str | None:
        async with self.client.execute(
            "SELECT name FROM mydb.users WHERE id=%s", (uid,)
        ) as result:
            if result.error:
                raise result.error
            row = await result.fetch_one()
            return row[0] if row else None

engine = Engine(url)
repo = UserRepo(engine)  # 构造式单例：同 (子类, 引擎) 恒返回同一实例
```

- 构造只收 `Engine`（无 database 参数，SQL 用全限定表名）；`self.client` 暴露引擎。
- `__new__` / `__init__` / `client` 均 `@final`，禁止重写。
- `release(engine=None)`（classmethod）：确定性注销实例表条目，**不负责 disconnect**；传 engine 删该引擎全部条目，不传清空全表。
- 推荐 shutdown 顺序：`await engine.disconnect()` 后 `UserRepo.release(engine)`。

## 错误语义

- `result.error`：`MySQLError | None`；`result.error_no`：无错误为 0；`result.error_msg`：无错误为空串。
- **取数前必须检查 `result.error`**；错误时 fetch 家族静默返回 None/[]，iterate 返空。
- **首错优先**：执行/COMMIT/ROLLBACK 三处错误收敛，后续错误不覆盖原始错误。
- `MySQLError` 后禁止盲目重试（语句可能已达服务端）；非 `MySQLError` 重抛且不置位 executed（允许重试）。
- 排查用 `error_no` / `error_msg` / `query`；存储的异常 traceback 已清空（断开引用环），不依赖原始栈。
- `row_count` / `last_rowid`：错误时返回 None。