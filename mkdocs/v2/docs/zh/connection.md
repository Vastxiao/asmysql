# 连接管理

## 连接配置

### 使用 URL 连接字符串

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

### 使用关键字参数

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
    result_class=tuple,
    init_sql=None,  # 可选：连接初始化时自动执行的 SET SQL
)
```

### 连接参数说明

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
| `init_sql` | str | `None` | 连接初始化时自动执行的 SET SQL（每条新 TCP 连接首次 acquire 时执行一次） |

## 连接和断开

### 方式一：显式连接

```python
from asmysql import Engine

engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")

# 连接
await engine.connect()
# ... 使用 engine
await engine.disconnect()
```

### 方式二：使用上下文管理器

```python
from asmysql import Engine

engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")

async with engine:
    # ... 使用 engine
    pass  # 自动断开连接
```

### 方式三：使用 await

```python
from asmysql import Engine

engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")

await engine()  # 等同于 await engine.connect()
```

## 检查连接状态

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

## 释放连接

```python
# 释放连接池中所有空闲连接
await engine.release_connections()
```

## 连接初始化 SQL（init_sql）

`init_sql` 参数用于在每条新 TCP 连接首次被使用时自动执行预设 SQL。适用于需要在连接级别设置 session 变量的场景，例如 ClickHouse 异步插入配置、MySQL session 变量等。

### 工作原理

- `connect()` 创建连接池后，自动包装 `pool.acquire()`
- 使用 `WeakSet` 追踪已初始化的连接对象
- 新连接首次 acquire 时执行 `init_sql`，后续复用同一连接时跳过
- 连接被 `pool_recycle` 回收重建后，新连接会重新执行 `init_sql`

### ClickHouse 异步插入配置

```python
from asmysql import Engine

engine = Engine(
    host="192.168.62.195",
    port=9004,
    user="default",
    password="",
    init_sql=(
        "SET async_insert = 1, wait_for_async_insert = 0, "
        "async_insert_busy_timeout_ms = 1000, "
        "max_execution_time = 30, max_memory_usage_for_user = 5368709120"
    ),
)
await engine.connect()

# 后续所有 execute 自动对新连接执行 SET，无需手动设置
async with engine.execute("INSERT INTO audit_log ...") as result:
    pass
```

### MySQL Session 变量

```python
from asmysql import Engine

engine = Engine(
    url="mysql://root:pass@127.0.0.1:3306/",
    init_sql="SET SESSION wait_timeout = 600, SESSION interactive_timeout = 600",
)
await engine.connect()
```

