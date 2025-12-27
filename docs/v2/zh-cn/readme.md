# asmysql v2 技术文档

[![PyPI](https://img.shields.io/pypi/v/asmysql.svg?logo=pypi&logoColor=FFE873)](https://pypi.org/project/asmysql/)
[![Python](https://img.shields.io/pypi/pyversions/asmysql.svg?logo=python&logoColor=FFE873)](https://pypi.org/project/asmysql/)
[![Licence](https://img.shields.io/github/license/Vastxiao/asmysql.svg)](https://github.com/Vastxiao/asmysql/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/badge/asmysql)](https://pepy.tech/project/asmysql)
[![Downloads](https://static.pepy.tech/badge/asmysql/month)](https://pepy.tech/project/asmysql)
[![Downloads](https://static.pepy.tech/badge/asmysql/week)](https://pepy.tech/project/asmysql)

* PyPI: https://pypi.org/project/asmysql/
* GitHub: https://github.com/vastxiao/asmysql
* Gitee: https://gitee.com/vastxiao/asmysql

## 目录

- [简介](#简介)
- [特性](#特性)
- [安装](#安装)
- [快速开始](#快速开始)
- [核心概念](#核心概念)
- [详细使用指南](#详细使用指南)
- [API 参考](#api-参考)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

## 简介

`asmysql` 是一个基于 `aiomysql` 封装的异步 MySQL 客户端库，专为 Python 异步编程设计。v2 版本完全重构了架构，提供了更清晰、更灵活的 API 设计，支持类型提示、连接池管理、错误处理等企业级特性。

### 主要优势

- **简单易用**：直观的 API 设计，学习成本低
- **类型安全**：完整的类型提示支持，提升开发体验
- **高性能**：基于连接池的异步操作，支持高并发
- **灵活扩展**：分离引擎和业务逻辑，便于架构设计
- **内存友好**：支持流式查询，处理大数据集不占用内存

## 特性

### v2 版本核心特性

1. **分离式架构**
   - `Engine` 类：独立的 MySQL 连接引擎，可单独使用
   - `AsMysql` 类：业务逻辑开发基类，继承即可使用
   - `Result` 类：结果处理类，支持多种数据获取方式

2. **连接管理**
   - 自动管理 MySQL 连接池
   - 支持连接池配置（最小/最大连接数）
   - 自动重连机制
   - 连接状态监控

3. **灵活的查询方式**
   - 支持普通查询和流式查询
   - 支持单条和批量执行
   - 支持事务控制

4. **多种结果类型**
   - `tuple`：默认元组类型
   - `dict`：字典类型
   - 自定义模型：支持 Pydantic 等模型类

5. **数据获取方式**
   - `fetch_one()`：获取单条记录
   - `fetch_many()`：获取多条记录
   - `fetch_all()`：获取所有记录
   - `iterate()`：异步迭代器，逐行获取
   - 直接迭代：`async for item in result`

6. **错误处理**
   - 全局自动捕获 `MysqlError`
   - 错误码和错误信息访问
   - 优雅的错误处理机制

7. **上下文管理**
   - 支持 `async with` 语法
   - 自动资源清理
   - 支持异步迭代器协议

8. **URL 连接字符串**
   - 支持 MySQL URL 格式连接
   - 格式：`mysql://user:password@host:port/?charset=utf8mb4`

## 安装

### 从 PyPI 安装

```bash
pip install asmysql
```

### 从源码安装

```bash
git clone https://github.com/vastxiao/asmysql.git
cd asmysql
pip install .
```

### 依赖要求

- Python >= 3.9
- aiomysql[rsa] >= 0.3.2

## 快速开始

### 方式一：使用 Engine 类

`Engine` 类是独立的 MySQL 连接引擎，可以直接使用：

```python
import asyncio
from asmysql import Engine

# 创建 MySQL 连接引擎
engine = Engine(url="mysql://root:pass@127.0.0.1:3306/?charset=utf8mb4")

async def main():
    # 连接 MySQL
    await engine.connect()
    
    # 执行 SQL 语句
    async with engine.execute("SELECT user, host FROM mysql.user") as result:
        async for item in result.iterate():
            print(item)
    
    # 断开 MySQL 连接
    await engine.disconnect()

asyncio.run(main())
```

### 方式二：使用 AsMysql 类

`AsMysql` 类用于业务逻辑开发，继承后可直接使用：

```python
import asyncio
from asmysql import Engine, AsMysql

# 创建 MySQL 连接引擎
engine = Engine(url="mysql://root:pass@127.0.0.1:3306/?charset=utf8mb4")

# 编写业务逻辑类
class UserService(AsMysql):
    async def get_all_users(self):
        result = await self.client.execute("SELECT user, host FROM mysql.user")
        if result.error:
            print(f"错误码: {result.error_no}, 错误信息: {result.error_msg}")
        else:
            async for item in result.iterate():
                print(item)

async def main():
    # 连接 MySQL
    await engine.connect()
    
    # 创建业务逻辑实例
    user_service = UserService(engine)
    
    # 执行业务逻辑
    await user_service.get_all_users()
    
    # 断开 MySQL 连接
    await engine.disconnect()

asyncio.run(main())
```

## 核心概念

### Engine（引擎）

`Engine` 是 MySQL 连接的核心类，负责：

- 管理连接池
- 执行 SQL 语句
- 处理连接生命周期

### AsMysql（业务逻辑类）

`AsMysql` 是业务逻辑开发的基类，提供：

- `client` 属性：访问 `Engine` 实例
- 业务方法封装
- 代码组织能力

### Result（结果类）

`Result` 是 SQL 执行结果的封装类，提供：

- 数据获取方法
- 错误信息访问
- 执行统计信息
- 异步迭代支持

## 详细使用指南

### 连接配置

#### 使用 URL 连接字符串

```python
from asmysql import Engine

# 基本 URL
engine = Engine(url="mysql://root:pass@127.0.0.1:3306/?charset=utf8mb4")

# 完整 URL（包含所有参数）
engine = Engine(
    url="mysql://root:pass@127.0.0.1:3306/"
    "?charset=utf8mb4"
    "&min_pool_size=2"
    "&max_pool_size=20"
    "&pool_recycle=3600"
    "&connect_timeout=10"
    "&auto_commit=true"
    "&echo_sql_log=false"
)
```

#### 使用关键字参数

```python
from asmysql import Engine

engine = Engine(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="pass",
    charset="utf8mb4",
    min_pool_size=1,
    max_pool_size=10,
    pool_recycle=-1,
    connect_timeout=5,
    auto_commit=True,
    echo_sql_log=False,
    stream=False,
    result_class=tuple
)
```

#### 连接参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `host` | str | `"127.0.0.1"` | MySQL 服务器地址 |
| `port` | int | `3306` | MySQL 服务器端口 |
| `user` | str | `""` | 用户名 |
| `password` | str | `""` | 密码 |
| `charset` | str | `"utf8mb4"` | 字符集 |
| `min_pool_size` | int | `1` | 连接池最小连接数 |
| `max_pool_size` | int | `10` | 连接池最大连接数 |
| `pool_recycle` | float | `-1` | 空闲连接回收时间（秒），-1 表示不回收 |
| `connect_timeout` | int | `5` | 连接超时时间（秒） |
| `auto_commit` | bool | `True` | 是否自动提交事务 |
| `echo_sql_log` | bool | `False` | 是否打印 SQL 日志 |
| `stream` | bool | `False` | 是否使用流式返回结果 |
| `result_class` | type | `tuple` | 返回结果类型 |

### 连接管理

#### 连接和断开

```python
from asmysql import Engine

engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")

# 方式一：显式连接
await engine.connect()
# ... 使用 engine
await engine.disconnect()

# 方式二：使用上下文管理器
async with engine:
    # ... 使用 engine
    pass  # 自动断开连接

# 方式三：使用 await
await engine()  # 等同于 await engine.connect()
```

#### 检查连接状态

```python
from asmysql import Engine

engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")

# 检查是否已连接
if engine.is_connected:
    print("已连接")

# 获取连接状态信息
await engine.connect()
status = engine.status
print(f"地址: {status['address']}")
print(f"已连接: {status['connected']}")
print(f"连接池大小: {status['pool_size']}")
print(f"空闲连接: {status['pool_free']}")
print(f"使用中连接: {status['pool_used']}")
```

#### 释放连接

```python
# 释放连接池中所有空闲连接
await engine.release_connections()
```

### 执行 SQL 语句

#### 基本查询

```python
from asmysql import Engine

engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")
await engine.connect()

# 方式一：使用 await
result = await engine.execute("SELECT * FROM users WHERE id = %s", (1,))
data = await result.fetch_one()

# 方式二：使用上下文管理器
async with engine.execute("SELECT * FROM users") as result:
    data = await result.fetch_all()

# 方式三：直接迭代
async for row in engine.execute("SELECT * FROM users"):
    print(row)
```

#### 参数化查询

```python
# 使用元组参数
result = await engine.execute(
    "SELECT * FROM users WHERE name = %s AND age > %s",
    ("张三", 18)
)

# 使用字典参数
result = await engine.execute(
    "SELECT * FROM users WHERE name = %(name)s AND age > %(age)s",
    {"name": "张三", "age": 18}
)
```

#### 批量执行

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

#### 流式查询

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

### 获取结果数据

#### fetch_one() - 获取单条记录

```python
result = await engine.execute("SELECT * FROM users WHERE id = %s", (1,))
user = await result.fetch_one()
if user:
    print(user)
```

#### fetch_many() - 获取多条记录

```python
result = await engine.execute("SELECT * FROM users")
users = await result.fetch_many(10)  # 获取 10 条记录
for user in users:
    print(user)
```

#### fetch_all() - 获取所有记录

```python
result = await engine.execute("SELECT * FROM users")
all_users = await result.fetch_all()
print(f"共 {len(all_users)} 条记录")
```

#### iterate() - 异步迭代器

```python
result = await engine.execute("SELECT * FROM users")
async for user in result.iterate():
    print(user)
```

#### 直接迭代 Result

```python
# 方式一：直接迭代 execute 返回的结果
async for user in engine.execute("SELECT * FROM users"):
    print(user)

# 方式二：先 await 再迭代
result = await engine.execute("SELECT * FROM users")
async for user in result:
    print(user)
```

### 结果类型

#### 默认 tuple 类型

```python
result = await engine.execute("SELECT id, name, email FROM users")
user = await result.fetch_one()
# user 是 tuple: (1, "张三", "zhangsan@example.com")
```

#### dict 类型

```python
result = await engine.execute(
    "SELECT id, name, email FROM users",
    result_class=dict
)
user = await result.fetch_one()
# user 是 dict: {"id": 1, "name": "张三", "email": "zhangsan@example.com"}
```

#### 自定义模型类型

```python
from pydantic import BaseModel
from asmysql import Engine

class User(BaseModel):
    id: int
    name: str
    email: str

engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")
await engine.connect()

result = await engine.execute(
    "SELECT id, name, email FROM users",
    result_class=User
)
user = await result.fetch_one()
# user 是 User 实例
print(user.name)  # 使用属性访问
```

### 错误处理

#### 检查错误

```python
result = await engine.execute("SELECT * FROM non_existent_table")
if result.error:
    print(f"错误码: {result.error_no}")
    print(f"错误信息: {result.error_msg}")
    print(f"错误对象: {result.error}")
else:
    data = await result.fetch_all()
```

#### 错误属性

- `result.error`：错误异常对象（`MySQLError` 或 `None`）
- `result.error_no`：错误码（整数，无错误时为 0）
- `result.error_msg`：错误信息（字符串，无错误时为空字符串）

### 执行统计信息

```python
result = await engine.execute("INSERT INTO users (name) VALUES (%s)", ("张三",))

# 受影响的行数
print(f"受影响行数: {result.row_count}")

# 最后插入的 ID（仅 INSERT 语句）
print(f"最后插入 ID: {result.last_rowid}")

# 当前游标位置
print(f"游标位置: {result.row_number}")
```

**注意**：
- `row_count` 在流式查询（`stream=True`）时返回 `None`
- `row_count` 在发生错误时返回 `None`
- `last_rowid` 仅在 INSERT 语句时有效

### 事务控制

#### 自动提交（默认）

```python
engine = Engine(
    url="mysql://root:pass@127.0.0.1:3306/",
    auto_commit=True  # 默认值
)
await engine.connect()

# 自动提交
result = await engine.execute("INSERT INTO users (name) VALUES (%s)", ("张三",))
```

#### 手动提交

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

### 业务逻辑开发

#### 继承 AsMysql 类

```python
from asmysql import Engine, AsMysql

class UserService(AsMysql):
    async def get_user_by_id(self, user_id: int):
        result = await self.client.execute(
            "SELECT * FROM users WHERE id = %s",
            (user_id,),
            result_class=dict
        )
        if result.error:
            return None
        return await result.fetch_one()

    async def create_user(self, name: str, email: str):
        result = await self.client.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            (name, email)
        )
        if result.error:
            raise Exception(f"创建用户失败: {result.error_msg}")
        return result.last_rowid

    async def list_users(self):
        result = await self.client.execute(
            "SELECT * FROM users",
            result_class=dict
        )
        if result.error:
            return []
        return await result.fetch_all()

# 使用
engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")
await engine.connect()

user_service = UserService(engine)
user = await user_service.get_user_by_id(1)
users = await user_service.list_users()
```

## API 参考

详细的 API 参考文档请查看 [API_zh.md](./API_zh.md)。

## 最佳实践

### 1. 连接管理

```python
# ✅ 推荐：使用上下文管理器
async with engine:
    result = await engine.execute("SELECT * FROM users")
    data = await result.fetch_all()

# ❌ 不推荐：忘记断开连接
await engine.connect()
result = await engine.execute("SELECT * FROM users")
# 忘记 await engine.disconnect()
```

### 2. 错误处理

```python
# ✅ 推荐：检查错误
result = await engine.execute("SELECT * FROM users")
if result.error:
    logger.error(f"查询失败: {result.error_msg}")
    return []
return await result.fetch_all()

# ❌ 不推荐：忽略错误
result = await engine.execute("SELECT * FROM users")
data = await result.fetch_all()  # 如果出错，data 可能是空列表
```

### 3. 大数据集处理

```python
# ✅ 推荐：使用流式查询
async for row in engine.execute("SELECT * FROM large_table", stream=True):
    process(row)

# ❌ 不推荐：一次性加载所有数据
data = await engine.execute("SELECT * FROM large_table")
all_data = await data.fetch_all()  # 可能内存溢出
```

### 4. 参数化查询

```python
# ✅ 推荐：使用参数化查询防止 SQL 注入
result = await engine.execute(
    "SELECT * FROM users WHERE name = %s",
    (user_name,)
)

# ❌ 不推荐：字符串拼接
result = await engine.execute(
    f"SELECT * FROM users WHERE name = '{user_name}'"
)
```

### 5. 连接池配置

```python
# ✅ 推荐：根据应用负载配置连接池
engine = Engine(
    url="mysql://root:pass@127.0.0.1:3306/",
    min_pool_size=5,   # 保持最小连接数
    max_pool_size=50,  # 根据并发量设置最大值
    pool_recycle=3600  # 1 小时回收空闲连接
)

# ❌ 不推荐：使用默认值（可能不适合生产环境）
engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")
```

## 常见问题

### Q: 如何查看连接池状态？

A: 使用 `engine.status` 属性：

```python
status = engine.status
print(status)
```

### Q: 流式查询和普通查询的区别？

A:
- **普通查询**：将所有结果加载到内存，适合小数据集
- **流式查询**：逐行返回结果，不占用内存，适合大数据集

### Q: 如何自定义结果类型？

A: 使用 `result_class` 参数，支持 `tuple`、`dict` 或自定义模型类：

```python
result = await engine.execute(
    "SELECT * FROM users",
    result_class=dict  # 或自定义模型类
)
```

### Q: 如何处理事务？

A: 设置 `auto_commit=False` 并手动管理：

```python
engine = Engine(url="...", auto_commit=False)
await engine.connect()

# 注意：v2 版本的事务管理需要手动控制连接
```

### Q: 错误信息如何获取？

A: 通过 `result.error`、`result.error_no` 和 `result.error_msg` 属性：

```python
result = await engine.execute("SELECT * FROM invalid_table")
if result.error:
    print(f"错误码: {result.error_no}")
    print(f"错误信息: {result.error_msg}")
```

### Q: 如何批量插入数据？

A: 使用 `execute_many()` 方法：

```python
data = [("张三", "zhangsan@example.com"), ("李四", "lisi@example.com")]
result = await engine.execute_many(
    "INSERT INTO users (name, email) VALUES (%s, %s)",
    data
)
```

## 更多资源

- [API 参考文档](./API.md)
- [使用示例](./EXAMPLES.md)
- [变更日志](./CHANGELOG.md)
- [GitHub 仓库](https://github.com/vastxiao/asmysql)
- [Gitee 仓库](https://gitee.com/vastxiao/asmysql)

