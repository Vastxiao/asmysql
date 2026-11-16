# asmysql 避坑清单

> 本文件是 asmysql-dev skill 的本地参考，SKILL.md 第 4 节 Top 5 的展开版。
> 使用前必须先完成 SKILL.md 第 1 节的版本自检；版本不匹配时改读包内 skill 或在线来源。

## 1. execute() 返回 Result，不是协程

`execute()` / `execute_many()` 返回懒执行 `Result` 对象，未实现 `__await__`；实际执行发生在 `async with` / `async for`。

```python
# 错误：TypeError，Result 不可 await
result = await engine.execute("SELECT 1")

# 正确：async with 触发执行并管理连接生命周期
async with engine.execute("SELECT 1") as result:
    row = await result.fetch_one()

# 正确：async for 直接遍历（懒执行 + 自动释放）
async for row in engine.execute("SELECT id FROM mydb.t"):
    ...
```

## 2. 取数前不检查 result.error，错误被静默吞掉

错误不抛异常，收敛在 `result.error`；错误时 fetch 家族返回 None/[]，`iterate()` 返空伪装 0 行。

```python
# 错误：表不存在/语法错误时 rows 为空列表，业务误判「没有数据」
async with engine.execute("SELECT * FROM mydb.not_exist") as result:
    rows = await result.fetch_all()

# 正确：先检查错误再取数
async with engine.execute("SELECT * FROM mydb.not_exist") as result:
    if result.error:
        logger.error("sql failed: %s %s", result.error_no, result.error_msg)
        raise result.error
    rows = await result.fetch_all()
```

## 3. 大结果集不用 stream=True，内存暴涨

默认缓冲游标一次性拉取全量行；v1 缓冲游标在大表场景会内存暴涨，v2 同样应流式读取。

```python
# 错误：千万行全量进内存
async with engine.execute("SELECT * FROM mydb.big_table") as result:
    rows = await result.fetch_all()

# 正确：流式逐行处理（SSCursor/SSDictCursor）
async for row in engine.execute("SELECT * FROM mydb.big_table", stream=True):
    process(row)
```

注意：流式结果集必须读完或显式 close（`async with` / `async for` 含 break 均自动处理），未读完的连接不可复用。

## 4. 误以为支持跨语句事务

每条 execute 是独立提交单元（autocommit=True + 事务状态兜底），**不支持跨语句事务**；不要写 BEGIN/COMMIT 配对业务。

```python
# 错误：两条语句不在同一事务，第一条失败第二条仍会执行并提交
async with engine.execute("UPDATE mydb.account SET balance=balance-100 WHERE id=1") as r1:
    ...
async with engine.execute("UPDATE mydb.account SET balance=balance+100 WHERE id=2") as r2:
    ...

# 正确：需要原子性时合并为单条语句，或在业务层做幂等/补偿
async with engine.execute(
    "UPDATE mydb.account SET balance = balance + CASE id WHEN 1 THEN -100 WHEN 2 THEN 100 END "
    "WHERE id IN (1, 2)"
) as result:
    if result.error:
        raise result.error
```

## 5. 活池跨事件循环共享

活池只属于创建它的事件循环（aiomysql 硬约束）；在新循环使用未断开的池会抛 `ConnectionError`。

```python
# 错误：全局 engine 在 asyncio.run() 之间复用活池
engine = Engine(url)
asyncio.run(job_a(engine))  # connect 后未 disconnect
asyncio.run(job_b(engine))  # 新循环访问活池 → ConnectionError

# 正确：每个循环内完成 connect/disconnect 闭环
async def job():
    async with Engine(url) as engine:
        ...
asyncio.run(job())
asyncio.run(job())  # 原循环已 disconnect，可安全复用引擎对象
```

## 补充陷阱

### execute_many([]) 发 UserWarning

空参数组不 acquire、不发 SQL，发 `UserWarning` 且 `row_count=0`；批量写入前先判空。

```python
# 错误：空列表触发 UserWarning，误以为写入成功
await engine.execute_many(sql, [])  # 且注意 execute_many 同样不可 await

# 正确：先判空
if rows:
    async with engine.execute_many(sql, rows) as result:
        if result.error:
            raise result.error
```

### MySQLError 后禁止盲目重试

`MySQLError` 置位 executed——语句可能已达服务端（如写入成功但响应超时），盲目重试会造成重复写入。先查 `error_no`/`error_msg` 判定错误类型，幂等语句才可重试；非 `MySQLError`（如网络未达）重抛且不置位，允许重试。

### disconnect_timeout=None 默认无限等待

`disconnect()` 默认无限等待未归还连接；仍被引用且未 close 的 Result 会挂住 shutdown。生产建议配置兜底：

```python
# 推荐：有限超时，超时 terminate 强制收敛（发 ResourceWarning）
engine = Engine(url, disconnect_timeout=10)
```

并坚持标准用法白名单（`async with` / `async for` / `fetch_all()` / `iterate()`），避免裸执行后不 close。

### v1 与 v2 错误字段名差异

v1 `Result.err`（属性）/ `err_msg`；v2 `Result.error` / `error_no` / `error_msg`。迁移代码时勿混用：

```python
# v1（冻结旧版）
if result.err:
    ...

# v2（新代码一律用这个）
if result.error:
    ...
```