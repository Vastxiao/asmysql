# asmysql v2 API 参考文档

本文档详细说明 asmysql v2 版本的所有 API。

## 导航

- [Engine 类](#engine)
- [AsMysql 类](#asmysql)
- [Result 类](#result)
- [类型定义](#type-definitions)

## Engine 类

`Engine` 是 MySQL 连接引擎类，负责管理连接池和执行 SQL 语句。

### 类定义

```python
class Engine:
    """异步的数据库 aiomysql 封装类"""
```

### 类属性（默认值）

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `host` | `str` | `"127.0.0.1"` | MySQL 服务器地址 |
| `port` | `int` | `3306` | MySQL 服务器端口 |
| `user` | `str` | `""` | 用户名 |
| `password` | `str` | `""` | 密码 |
| `charset` | `str` | `"utf8mb4"` | 字符集 |
| `min_pool_size` | `int` | `1` | 连接池最小连接数 |
| `max_pool_size` | `int` | `10` | 连接池最大连接数 |
| `pool_recycle` | `float` | `-1` | 空闲连接回收时间（秒），-1 表示不回收 |
| `connect_timeout` | `int` | `5` | 连接超时时间（秒） |
| `auto_commit` | `bool` | `True` | 是否自动提交事务 |
| `echo_sql_log` | `bool` | `False` | 是否打印 SQL 日志 |
| `stream` | `bool` | `False` | 是否使用流式返回结果 |
| `result_class` | `type` | `tuple` | 返回结果类型 |

### 构造函数

```python
def __init__(
    self,
    url: str = None,
    *,
    host: str = None,
    port: int = None,
    user: str = None,
    password: str = None,
    charset: str = None,
    min_pool_size: int = None,
    max_pool_size: int = None,
    pool_recycle: float = None,
    connect_timeout: int = None,
    auto_commit: bool = None,
    echo_sql_log: bool = None,
    stream: bool = None,
    result_class: type = None,
) -> None
```

**参数说明**：

- `url` (str, optional): MySQL 连接 URL，格式：`mysql://user:password@host:port/?charset=utf8mb4`
- `host` (str, optional): MySQL 服务器地址
- `port` (int, optional): MySQL 服务器端口
- `user` (str, optional): 用户名
- `password` (str, optional): 密码
- `charset` (str, optional): 字符集
- `min_pool_size` (int, optional): 连接池最小连接数
- `max_pool_size` (int, optional): 连接池最大连接数
- `pool_recycle` (float, optional): 空闲连接回收时间（秒）
- `connect_timeout` (int, optional): 连接超时时间（秒）
- `auto_commit` (bool, optional): 是否自动提交事务
- `echo_sql_log` (bool, optional): 是否打印 SQL 日志
- `stream` (bool, optional): 是否使用流式返回结果
- `result_class` (type, optional): 返回结果类型

**示例**：

```python
# 使用 URL
engine = Engine(url="mysql://root:pass@127.0.0.1:3306/?charset=utf8mb4")

# 使用关键字参数
engine = Engine(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="pass",
    charset="utf8mb4"
)
```

### 方法

#### connect()

连接到 MySQL，建立 TCP 连接，初始化连接池。

```python
async def connect(self) -> Engine
```

**返回值**：返回 `self`，支持链式调用

**示例**：

```python
await engine.connect()
```

#### disconnect()

等待所有连接释放，并正常关闭 MySQL 连接。

```python
async def disconnect(self) -> None
```

**示例**：

```python
await engine.disconnect()
```

#### release_connections()

释放连接池中所有空闲的连接。

```python
async def release_connections(self) -> None
```

**示例**：

```python
await engine.release_connections()
```

#### execute()

执行 SQL 语句并返回 Result 对象。

```python
def execute(
    self,
    query: str,
    values: Union[Sequence, dict] = None,
    *,
    stream: bool = None,
    result_class: type[T] = None,
    commit: bool = None,
) -> Union[Awaitable[Result[T]], AsyncContextManager[Result[T]], AsyncGenerator[T, None]]
```

**参数说明**：

- `query` (str): SQL 语句
- `values` (Union[Sequence, dict], optional): 参数，可以是元组或字典
- `stream` (bool, optional): 是否流式返回结果，默认使用 `self.stream`
- `result_class` (type, optional): 结果类型，默认使用 `self.result_class`
- `commit` (bool, optional): 是否提交事务，默认使用 `self.auto_commit`

**返回值**：返回 `Result` 对象，支持以下用法：

1. `result = await engine.execute(...)`
2. `async with engine.execute(...) as result:`
3. `async for item in engine.execute(...):`

**示例**：

```python
# 方式一：await
result = await engine.execute("SELECT * FROM users WHERE id = %s", (1,))
data = await result.fetch_one()

# 方式二：上下文管理器
async with engine.execute("SELECT * FROM users") as result:
    data = await result.fetch_all()

# 方式三：直接迭代
async for row in engine.execute("SELECT * FROM users"):
    print(row)
```

#### execute_many()

批量执行 SQL 语句并返回 Result 对象。

```python
def execute_many(
    self,
    query: str,
    values: Sequence[Union[Sequence, dict]],
    *,
    stream: bool = None,
    result_class: type[T] = None,
    commit: bool = None,
) -> Union[Awaitable[Result[T]], AsyncContextManager[Result[T]], AsyncGenerator[T, None]]
```

**参数说明**：

- `query` (str): SQL 语句
- `values` (Sequence[Union[Sequence, dict]]): 参数列表，每个元素可以是元组或字典
- `stream` (bool, optional): 是否流式返回结果
- `result_class` (type, optional): 结果类型
- `commit` (bool, optional): 是否提交事务

**返回值**：返回 `Result` 对象

**示例**：

```python
data = [
    ("张三", "zhangsan@example.com"),
    ("李四", "lisi@example.com")
]
result = await engine.execute_many(
    "INSERT INTO users (name, email) VALUES (%s, %s)",
    data
)
```

### 属性

#### status

返回数据库连接池状态。

```python
@property
def status(self) -> EngineStatus
```

**返回值**：`EngineStatus` 字典，包含以下字段：

- `address` (str): 连接地址
- `connected` (bool): 是否已连接
- `pool_minsize` (Optional[int]): 连接池最小大小
- `pool_maxsize` (Optional[int]): 连接池最大大小
- `pool_size` (Optional[int]): 连接池当前大小
- `pool_free` (Optional[int]): 空闲连接数
- `pool_used` (Optional[int]): 使用中连接数

**示例**：

```python
status = engine.status
print(f"连接状态: {status['connected']}")
print(f"连接池大小: {status['pool_size']}")
```

#### is_connected

数据库是否已连接。

```python
@property
def is_connected(self) -> bool
```

**返回值**：`bool`，已连接返回 `True`，否则返回 `False`

**示例**：

```python
if engine.is_connected:
    print("已连接")
```

#### pool

获取连接池对象（内部使用）。

```python
@property
def pool(self) -> Pool
```

**返回值**：`aiomysql.Pool` 对象

**注意**：此属性仅供内部使用，如果未连接会抛出 `ConnectionError`

#### url

连接 URL（只读）。

```python
url: Final[str]
```

**示例**：

```python
print(engine.url)  # mysql://127.0.0.1:3306/
```

### 特殊方法

#### __aenter__() / __aexit__()

支持 `async with` 语法。

```python
async def __aenter__(self) -> Engine
async def __aexit__(self, exc_type, exc_value, exc_tb) -> None
```

**示例**：

```python
async with engine:
    result = await engine.execute("SELECT * FROM users")
    data = await result.fetch_all()
```

#### __await__()

支持 `await engine` 语法。

```python
def __await__(self) -> Generator[Any, None, Engine]
```

**示例**：

```python
await engine  # 等同于 await engine.connect()
```

#### __call__()

支持 `await engine()` 语法。

```python
async def __call__(self) -> Engine
```

**示例**：

```python
await engine()  # 等同于 await engine.connect()
```

## AsMysql 类

`AsMysql` 是业务逻辑开发的基类，用于封装业务方法。

### 类定义

```python
class AsMysql:
    """Mysql 编写业务逻辑的类"""
```

### 构造函数

```python
def __init__(self, engine: Engine) -> None
```

**参数说明**：

- `engine` (Engine): `Engine` 实例

**示例**：

```python
engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")
await engine.connect()

class UserService(AsMysql):
    pass

service = UserService(engine)
```

### 属性

#### client

访问 `Engine` 实例。

```python
@property
def client(self) -> Engine
```

**返回值**：`Engine` 实例

**示例**：

```python
class UserService(AsMysql):
    async def get_users(self):
        result = await self.client.execute("SELECT * FROM users")
        return await result.fetch_all()
```

## Result 类

`Result` 是 SQL 执行结果的封装类，提供数据获取和错误处理功能。

### 类定义

```python
class Result(Generic[T]):
    """SQL 执行结果类"""
```

### 构造函数

```python
def __init__(
    self,
    *,
    pool: Pool,
    query: str,
    values: Union[Sequence, dict] = None,
    execute_many: bool = False,
    stream: bool = False,
    commit: bool = True,
    result_class: T = tuple,
) -> None
```

**参数说明**（内部使用，通常不需要直接构造）：

- `pool` (Pool): 连接池对象
- `query` (str): SQL 语句
- `values` (Union[Sequence, dict], optional): 参数
- `execute_many` (bool): 是否批量执行
- `stream` (bool): 是否流式返回
- `commit` (bool): 是否提交事务
- `result_class` (type): 结果类型

### 方法

#### fetch_one()

获取一条记录。

```python
async def fetch_one(self, close: bool = None) -> Optional[T]
```

**参数说明**：

- `close` (bool, optional): 是否自动关闭游标连接。如果设置为 `False`，必须手动调用 `Result.close()` 释放连接

**返回值**：返回一条记录，如果没有数据则返回 `None`

**示例**：

```python
result = await engine.execute("SELECT * FROM users WHERE id = %s", (1,))
user = await result.fetch_one()
if user:
    print(user)
```

#### fetch_many()

获取多条记录。

```python
async def fetch_many(self, size: int = None, close: bool = None) -> list[T]
```

**参数说明**：

- `size` (int, optional): 获取记录的数量，默认获取所有可用记录
- `close` (bool, optional): 是否自动关闭游标连接

**返回值**：返回记录列表

**示例**：

```python
result = await engine.execute("SELECT * FROM users")
users = await result.fetch_many(10)  # 获取 10 条记录
```

#### fetch_all()

获取所有记录。

```python
async def fetch_all(self) -> list[T]
```

**返回值**：返回所有记录的列表

**注意**：此方法会自动关闭游标连接

**示例**：

```python
result = await engine.execute("SELECT * FROM users")
all_users = await result.fetch_all()
```

#### iterate()

异步生成器，遍历所有记录。

```python
async def iterate(self) -> AsyncGenerator[T, None]
```

**返回值**：异步生成器，逐行返回记录

**注意**：此方法会自动关闭游标连接

**示例**：

```python
result = await engine.execute("SELECT * FROM users")
async for user in result.iterate():
    print(user)
```

#### close()

关闭游标并释放连接。

```python
async def close(self) -> None
```

**示例**：

```python
result = await engine.execute("SELECT * FROM users")
data = await result.fetch_one(close=False)
# ... 其他操作
await result.close()  # 手动关闭
```

### 属性

#### error

错误异常对象。

```python
@property
def error(self) -> Optional[MySQLError]
```

**返回值**：`MySQLError` 异常对象，如果没有错误则返回 `None`

**示例**：

```python
result = await engine.execute("SELECT * FROM invalid_table")
if result.error:
    print(f"错误: {result.error}")
```

#### error_no

错误码。

```python
@property
def error_no(self) -> int
```

**返回值**：错误码（整数），如果没有错误则返回 `0`

**示例**：

```python
if result.error:
    print(f"错误码: {result.error_no}")
```

#### error_msg

错误信息。

```python
@property
def error_msg(self) -> str
```

**返回值**：错误信息（字符串），如果没有错误则返回空字符串

**示例**：

```python
if result.error:
    print(f"错误信息: {result.error_msg}")
```

#### row_count

受影响的行数。

```python
@property
def row_count(self) -> Optional[int]
```

**返回值**：
- 受影响的行数（整数）
- 如果发生错误，返回 `None`
- 如果使用流式查询（`stream=True`），返回 `None`

**示例**：

```python
result = await engine.execute("INSERT INTO users (name) VALUES (%s)", ("张三",))
print(f"插入了 {result.row_count} 条记录")
```

#### last_rowid

最近插入的记录的 ID。

```python
@property
def last_rowid(self) -> Optional[int]
```

**返回值**：
- 最近插入的记录的 ID（整数）
- 如果没有插入数据或发生错误，返回 `None`

**示例**：

```python
result = await engine.execute("INSERT INTO users (name) VALUES (%s)", ("张三",))
print(f"新插入的 ID: {result.last_rowid}")
```

#### row_number

当前游标的位置。

```python
@property
def row_number(self) -> Optional[int]
```

**返回值**：
- 当前游标在结果集中的行索引（从 0 开始）
- 如果无法确定索引或发生错误，返回 `None`

**示例**：

```python
result = await engine.execute("SELECT * FROM users")
while True:
    row = await result.fetch_one(close=False)
    if not row:
        break
    print(f"当前位置: {result.row_number}")
```

### 特殊方法

#### __aenter__() / __aexit__()

支持 `async with` 语法。

```python
async def __aenter__(self) -> Result[T]
async def __aexit__(self, exc_type, exc_value, exc_tb) -> None
```

**示例**：

```python
async with engine.execute("SELECT * FROM users") as result:
    data = await result.fetch_all()
```

#### __aiter__() / __anext__()

支持 `async for` 语法。

```python
def __aiter__(self) -> Result[T]
async def __anext__(self) -> T
```

**示例**：

```python
result = await engine.execute("SELECT * FROM users")
async for user in result:
    print(user)
```

#### __await__()

支持 `await result` 语法。

```python
def __await__(self) -> Generator[Any, None, Result[T]]
```

**示例**：

```python
result = await engine.execute("SELECT * FROM users")
# 等同于执行了 SQL 查询
```

#### __call__()

支持 `await result()` 语法。

```python
async def __call__(self) -> Result[T]
```

**示例**：

```python
result = engine.execute("SELECT * FROM users")
await result()  # 执行查询
data = await result.fetch_all()
```

## 类型定义 {#type-definitions}

### EngineStatus

连接引擎状态类型。

```python
class EngineStatus(TypedDict):
    address: str
    connected: bool
    pool_minsize: Optional[int]
    pool_maxsize: Optional[int]
    pool_size: Optional[int]
    pool_free: Optional[int]
    pool_used: Optional[int]
```

### 类型别名

```python
AsyncEngine = Engine
AsyncResult = Result
```

这些类型别名用于向后兼容或类型提示。

## 导入方式

```python
# 方式一：从主模块导入
from asmysql import Engine, AsMysql, Result

# 方式二：从 v2 子模块导入
from asmysql.v2 import Engine, AsMysql, Result

# 方式三：使用类型别名
from asmysql import AsyncEngine, AsyncResult
```

