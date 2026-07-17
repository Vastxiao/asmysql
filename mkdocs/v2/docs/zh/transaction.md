# 事务控制

## 自动提交机制

v2 版本采用基于 SQL 语句类型的自动提交机制。`Result` 内部通过 `_should_commit()` 方法分析 SQL 语句的首关键词，自动判断是否需要执行 `COMMIT`。

### 写操作自动提交

对于以下写操作关键词，执行后会自动提交：

- `INSERT`、`UPDATE`、`DELETE`、`REPLACE`
- `CREATE`、`ALTER`、`DROP`、`TRUNCATE`、`RENAME`
- `GRANT`、`REVOKE`、`LOCK`、`UNLOCK`
- `SET`、`LOAD`、`CALL`

```python
# 写操作自动提交，无需手动控制
async with engine.execute(
    "INSERT INTO users (name) VALUES (%s)", ("张三",)
) as result:
    pass  # 执行完毕后自动 COMMIT
```

### 读操作不提交

对于 `SELECT` 等读操作，不会执行 `COMMIT`，因为读操作不需要事务提交。

```python
# 读操作不会触发 COMMIT
async with engine.execute("SELECT * FROM users") as result:
    data = await result.fetch_all()
```

### 流式模式不提交

在 `stream=True` 模式下，即使是写操作也不会自动提交。这是因为流式模式下 `COMMIT` 会导致流中断。

```python
# 流式查询不会自动提交
async with engine.execute(
    "SELECT * FROM large_table",
    stream=True
) as result:
    async for row in result:
        process(row)
```

## 连接池配置

连接池创建时 `autocommit=False` 是硬编码的，这意味着：

- 每条连接默认不自动提交
- 事务提交由 `Result` 内部逻辑根据 SQL 类型自动处理
- 无需手动配置 `auto_commit` 参数

## 相关文档

- [查询操作](query.md) - 了解如何执行 SQL 语句
- [最佳实践](best-practices.md) - 了解推荐的使用方式
