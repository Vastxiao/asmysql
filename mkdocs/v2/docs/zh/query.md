# 查询操作

## 基本查询

### 方式一：使用 await

```python
from asmysql import Engine

engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")
await engine.connect()

result = await engine.execute("SELECT * FROM users WHERE id = %s", (1,))
data = await result.fetch_one()
```

### 方式二：使用上下文管理器

```python
from asmysql import Engine

engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")
await engine.connect()

async with engine.execute("SELECT * FROM users") as result:
    data = await result.fetch_all()
```

### 方式三：直接迭代

```python
from asmysql import Engine

engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")
await engine.connect()

async for row in engine.execute("SELECT * FROM users"):
    print(row)
```

## 参数化查询

### 使用元组参数

```python
result = await engine.execute(
    "SELECT * FROM users WHERE name = %s AND age > %s",
    ("张三", 18)
)
```

### 使用字典参数

```python
result = await engine.execute(
    "SELECT * FROM users WHERE name = %(name)s AND age > %(age)s",
    {"name": "张三", "age": 18}
)
```

## 批量执行

```python
# 批量插入
users = [
    ("张三", "zhangsan@example.com"),
    ("李四", "lisi@example.com"),
    ("王五", "wangwu@example.com")
]
result = await engine.execute_many(
    "INSERT INTO users (name, email) VALUES (%s, %s)",
    users
)
print(f"插入了 {result.row_count} 条记录")
```

## 流式查询

流式查询适用于大数据集，不会将所有数据加载到内存：

```python
# 启用流式查询
result = await engine.execute(
    "SELECT * FROM large_table",
    stream=True
)

# 流式迭代
async for row in result:
    process(row)  # 逐行处理，不占用内存
```

## 相关文档

- [结果处理](result.md) - 了解如何获取和处理查询结果
- [事务控制](transaction.md) - 了解事务管理

