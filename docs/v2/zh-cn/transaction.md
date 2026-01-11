# 事务控制

## 自动提交（默认）

```python
engine = Engine(
    url="mysql://root:pass@127.0.0.1:3306/",
    auto_commit=True  # 默认值
)
await engine.connect()

# 自动提交
result = await engine.execute("INSERT INTO users (name) VALUES (%s)", ("张三",))
```

## 手动提交

```python
engine = Engine(
    url="mysql://root:pass@127.0.0.1:3306/",
    auto_commit=False
)
await engine.connect()

# 不自动提交
result = await engine.execute(
    "INSERT INTO users (name) VALUES (%s)",
    ("张三",),
    commit=False
)

# 手动提交
await result.close()  # 需要手动管理连接
```

## 注意事项

v2 版本的事务管理需要手动控制连接。建议在生产环境中根据实际需求选择合适的提交策略。

## 相关文档

- [查询操作](query.md) - 了解如何执行 SQL 语句
- [最佳实践](best-practices.md) - 了解推荐的使用方式
