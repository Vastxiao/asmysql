# 常见问题

## Q: 如何查看连接池状态？

A: 使用 `engine.status` 属性：

```python
status = engine.status
print(status)
```

## Q: 流式查询和普通查询的区别？

A:
- **普通查询**：将所有结果加载到内存，适合小数据集
- **流式查询**：逐行返回结果，不占用内存，适合大数据集

## Q: 如何自定义结果类型？

A: 使用 `result_class` 参数，支持 `tuple`、`dict` 或自定义模型类：

```python
result = await engine.execute(
    "SELECT * FROM users",
    result_class=dict  # 或自定义模型类
)
```

## Q: 如何处理事务？

A: 设置 `auto_commit=False` 并手动管理：

```python
engine = Engine(url="...", auto_commit=False)
await engine.connect()

# 注意：v2 版本的事务管理需要手动控制连接
```

## Q: 错误信息如何获取？

A: 通过 `result.error`、`result.error_no` 和 `result.error_msg` 属性：

```python
result = await engine.execute("SELECT * FROM invalid_table")
if result.error:
    print(f"错误码: {result.error_no}")
    print(f"错误信息: {result.error_msg}")
```

## Q: 如何批量插入数据？

A: 使用 `execute_many()` 方法：

```python
data = [("张三", "zhangsan@example.com"), ("李四", "lisi@example.com")]
result = await engine.execute_many(
    "INSERT INTO users (name, email) VALUES (%s, %s)",
    data
)
```

## Q: 如何在不同模块间共享 Engine 实例？

A: 可以在应用启动时创建 Engine 实例，然后通过依赖注入或全局变量共享：

```python
# app.py
engine = Engine(url="mysql://...")
await engine.connect()

# service.py
from app import engine

class UserService(AsMysql):
    def __init__(self):
        super().__init__(engine)
```

## Q: 连接池大小如何设置？

A: 根据应用的并发量和数据库服务器的性能来设置：

- 低并发应用：`min_pool_size=2, max_pool_size=10`
- 中等并发：`min_pool_size=5, max_pool_size=50`
- 高并发应用：`min_pool_size=10, max_pool_size=100+`

## Q: 如何处理连接超时？

A: 可以通过 `connect_timeout` 参数设置连接超时时间：

```python
engine = Engine(
    url="mysql://...",
    connect_timeout=10  # 10 秒超时
)
```

## 相关文档

- [连接管理](connection.md) - 了解更多连接配置
- [最佳实践](best-practices.md) - 查看推荐的使用方式

