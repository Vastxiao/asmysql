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
    "&auto_commit=true"
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
    auto_commit=True,
    echo_sql_log=False,
    stream=False,
    result_class=tuple
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
| `auto_commit` | bool | `True` | Whether to auto-commit transactions |
| `echo_sql_log` | bool | `False` | Whether to print SQL logs |
| `stream` | bool | `False` | Whether to use streaming result |
| `result_class` | type | `tuple` | Result type |

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

