# 结果处理

## 获取结果数据

### fetch_one() - 获取单条记录

```python
async with engine.execute("SELECT * FROM users WHERE id = %s", (1,)) as result:
    user = await result.fetch_one()
    if user:
        print(user)
```

### fetch_many() - 获取多条记录

```python
async with engine.execute("SELECT * FROM users") as result:
    users = await result.fetch_many(10)  # 获取 10 条记录
    for user in users:
        print(user)
```

### fetch_all() - 获取所有记录

```python
async with engine.execute("SELECT * FROM users") as result:
    all_users = await result.fetch_all()
    print(f"共 {len(all_users)} 条记录")
```

### iterate() - 异步迭代器

```python
async with engine.execute("SELECT * FROM users") as result:
    async for user in result.iterate():
        print(user)
```

### 直接迭代 Result

```python
# 方式一：直接迭代 execute 返回的结果
async for user in engine.execute("SELECT * FROM users"):
    print(user)

# 方式二：使用 async with 再迭代
async with engine.execute("SELECT * FROM users") as result:
    async for user in result:
        print(user)
```

## 结果类型

### 默认 tuple 类型

```python
async with engine.execute("SELECT id, name, email FROM users") as result:
    user = await result.fetch_one()
    # user 是 tuple: (1, "张三", "zhangsan@example.com")
```

### dict 类型

```python
async with engine.execute(
    "SELECT id, name, email FROM users",
    result_class=dict
) as result:
    user = await result.fetch_one()
    # user 是 dict: {"id": 1, "name": "张三", "email": "zhangsan@example.com"}
```

### 自定义模型类型

```python
from pydantic import BaseModel
from asmysql import Engine

class User(BaseModel):
    id: int
    name: str
    email: str

engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")
await engine.connect()

async with engine.execute(
    "SELECT id, name, email FROM users",
    result_class=User
) as result:
    user = await result.fetch_one()
    # user 是 User 实例
    print(user.name)  # 使用属性访问
```

## 错误处理

### 检查错误

```python
async with engine.execute("SELECT * FROM non_existent_table") as result:
    if result.error:
        print(f"错误码: {result.error_no}")
        print(f"错误信息: {result.error_msg}")
        print(f"错误对象: {result.error}")
    else:
        data = await result.fetch_all()
```

### 错误属性

- `result.error`：错误异常对象（`MySQLError` 或 `None`）
- `result.error_no`：错误码（整数，无错误时为 0）
- `result.error_msg`：错误信息（字符串，无错误时为空字符串）

## 执行统计信息

```python
async with engine.execute("INSERT INTO users (name) VALUES (%s)", ("张三",)) as result:
    # 受影响的行数
    print(f"受影响行数: {result.row_count}")

    # 最后插入的 ID（仅 INSERT 语句）
    print(f"最后插入 ID: {result.last_rowid}")
```

**注意**：
- `row_count` 在流式查询（`stream=True`）时返回 `None`
- `row_count` 在发生错误时返回 `None`
- `last_rowid` 仅在 INSERT 语句时有效
