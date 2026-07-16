# Connection Management

## Connection Configuration

### Using URL Connection String

```python
from asmysql import Engine

# Basic URL
engine = Engine(url="mysql://root:pass@127.0.0.1:3306/?charset=utf8mb4")

# Complete URL (with all parameters)
engine = Engine(
    url="mysql://root:pass@127.0.0.1:3306/"
    "?charset=utf8mb4"
    "&min_pool_size=2"
    "&max_pool_size=20"
    "&pool_recycle=3600"
    "&connect_timeout=10"
    "&echo_sql_log=false"
)
```

### Using Keyword Arguments

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
    echo_sql_log=False,
    result_class=tuple,
    init_sql=None,  # Optional: SET SQL to auto-execute on connection init
)
```

### Connection Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `host` | str | `"127.0.0.1"` | MySQL server address |
| `port` | int | `3306` | MySQL server port |
| `user` | str | `""` | Username |
| `password` | str | `""` | Password |
| `charset` | str | `"utf8mb4"` | Character set |
| `min_pool_size` | int | `1` | Minimum connection pool size |
| `max_pool_size` | int | `10` | Maximum connection pool size |
| `pool_recycle` | float | `-1` | Idle connection recycle time (seconds), -1 means no recycle |
| `connect_timeout` | int | `5` | Connection timeout (seconds) |
| `echo_sql_log` | bool | `False` | Whether to print SQL logs |
| `result_class` | type | `tuple` | Result type |
| `init_sql` | str | `None` | SET SQL to auto-execute on each new TCP connection's first use |

## Connect and Disconnect

### Method 1: Explicit Connection

```python
from asmysql import Engine

engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")

# Connect
await engine.connect()
# ... use engine
await engine.disconnect()
```

### Method 2: Using Context Manager

```python
from asmysql import Engine

engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")

async with engine:
    # ... use engine
    pass  # Automatically disconnect
```

### Method 3: Using await

```python
from asmysql import Engine

engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")

await engine()  # Equivalent to await engine.connect()
```

## Check Connection Status

```python
from asmysql import Engine

engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")

# Check if connected
if engine.is_connected:
    print("Connected")

# Get connection status information
await engine.connect()
status = engine.status
print(f"Address: {status['address']}")
print(f"Connected: {status['connected']}")
print(f"Pool size: {status['pool_size']}")
print(f"Free connections: {status['pool_free']}")
print(f"Used connections: {status['pool_used']}")
```

## Release Connections

```python
# Release all idle connections in the pool
await engine.release_connections()
```

## Connection Init SQL (init_sql)

The `init_sql` parameter automatically executes preset SQL on each new TCP connection's first use. Ideal for setting session-level variables, such as ClickHouse async insert settings or MySQL session variables.

### How It Works

- `init_sql` execution is implemented in `Result.__call__()`, not at `connect()` stage
- Uses `weakref.WeakKeyDictionary` with Pool as key to track initialized connection IDs
- Executes `init_sql` on first SQL execution of a new connection; skips on subsequent reuses
- When a connection is recycled via `pool_recycle`, the new connection re-executes `init_sql`

### ClickHouse Async Insert Configuration

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

# All subsequent execute() calls automatically run SET on new connections
async with engine.execute("INSERT INTO audit_log ...") as result:
    pass
```

### MySQL Session Variables

```python
from asmysql import Engine

engine = Engine(
    url="mysql://root:pass@127.0.0.1:3306/",
    init_sql="SET SESSION wait_timeout = 600, SESSION interactive_timeout = 600",
)
await engine.connect()
```

