# 最佳实践

## 1. 对于简单的mysql连接场景下，建议使用上下文管理

### ✅ 推荐：使用上下文管理器

```python
# 使用上下文管理器自动管理连接
async with engine:
    # 执行 SQL 语句 使用上下文管理器处理
    async with engine.execute("select user,host from mysql.user") as result:
        async for item in result.iterate():
            print(item)
    # 退出时自动断开 MySQL 连接
```

### ❌ 不推荐：忘记断开连接

```python
await engine.connect()
async with engine.execute("SELECT * FROM users") as result:
    pass
# 忘记 await engine.disconnect()
```

## 2. 关于连接资源管理

`execute()` / `execute_many()` 返回的 `Result` 对象必须通过 `async with` 或 `async for` 使用，以确保连接正确释放：

### ✅ 推荐：使用上下文管理器（自动管理连接）

使用 `async with` 时，连接会在退出上下文时自动关闭：

```python
async with engine.execute("SELECT * FROM users") as result:
    data = await result.fetch_one()
    # 退出时自动关闭连接
```

### ✅ 推荐：使用 `async for`（自动管理连接）

使用 `async for` 时，连接会在迭代完成后自动关闭：

```python
async for item in engine.execute("SELECT * FROM users"):
    print(item)
    # 迭代完成后自动关闭连接
```

### ⚠️ 注意：必须使用 async with 或 async for

`execute()` 返回的是 `Result` 对象（非协程），不能 `await`。必须通过 `async with` 或 `async for` 使用：

```python
# ✅ 正确：使用 async with
async with engine.execute("SELECT * FROM users") as result:
    data = await result.fetch_one()

# ✅ 正确：使用 async for
async for item in engine.execute("SELECT * FROM users"):
    print(item)

# ❌ 错误：不能 await（execute 不是协程）
# result = await engine.execute("SELECT * FROM users")
```

**重要提示**：
- `Result` 对象必须通过 `async with` 或 `async for` 使用，否则连接不会被归还到连接池
- 未正确关闭 `Result` 会导致 `ResourceWarning` 和连接泄漏
- 使用上下文管理器或 `async for` 时，连接由框架自动管理

## 3. 错误处理

### ✅ 推荐：检查错误

```python
async with engine.execute("SELECT * FROM users") as result:
    if result.error:
        logger.error(f"查询失败: {result.error_msg}")
        return []
    return await result.fetch_all()
```

### ❌ 不推荐：忽略错误

```python
async with engine.execute("SELECT * FROM users") as result:
    data = await result.fetch_all()  # 如果出错，data 可能是空列表
```

## 4. 大数据集处理

### ✅ 推荐：使用流式查询

```python
async for row in engine.execute("SELECT * FROM large_table", stream=True):
    process(row)
```

### ❌ 不推荐：一次性加载所有数据

```python
async with engine.execute("SELECT * FROM large_table") as result:
    all_data = await result.fetch_all()  # 可能内存溢出
```

## 5. 参数化查询

### ✅ 推荐：使用参数化查询防止 SQL 注入

```python
async with engine.execute(
    "SELECT * FROM users WHERE name = %s",
    (user_name,)
) as result:
    users = await result.fetch_all()
```

### ❌ 不推荐：字符串拼接

```python
async with engine.execute(
    f"SELECT * FROM users WHERE name = '{user_name}'"
) as result:
    users = await result.fetch_all()
```

## 6. 连接池配置

### ✅ 推荐：根据应用负载配置连接池

```python
engine = Engine(
    url="mysql://root:pass@127.0.0.1:3306/",
    min_pool_size=5,   # 保持最小连接数
    max_pool_size=50,  # 根据并发量设置最大值
    pool_recycle=3600  # 1 小时回收空闲连接
)
```

### ❌ 不推荐：使用默认值（可能不适合生产环境）

```python
engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")
```
