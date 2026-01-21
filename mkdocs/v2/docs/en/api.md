# asmysql v2 API Reference

This document details all APIs in asmysql v2 version.

## Navigation

- [Engine Class](#engine-class)
- [AsMysql Class](#asmysql-class)
- [Result Class](#result-class)
- [Type Definitions](#type-definitions)

## Engine Class

`Engine` is the MySQL connection engine class, responsible for managing connection pool and executing SQL statements.

### Class Definition

```python
class Engine:
    """Asynchronous database aiomysql wrapper class"""
```

### Class Attributes (Default Values)

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `host` | `str` | `"127.0.0.1"` | MySQL server address |
| `port` | `int` | `3306` | MySQL server port |
| `user` | `str` | `""` | Username |
| `password` | `str` | `""` | Password |
| `charset` | `str` | `"utf8mb4"` | Character set |
| `min_pool_size` | `int` | `1` | Minimum connection pool size |
| `max_pool_size` | `int` | `10` | Maximum connection pool size |
| `pool_recycle` | `float` | `-1` | Idle connection recycle time (seconds), -1 means no recycle |
| `connect_timeout` | `int` | `5` | Connection timeout (seconds) |
| `auto_commit` | `bool` | `True` | Whether to auto-commit transactions |
| `echo_sql_log` | `bool` | `False` | Whether to print SQL logs |
| `stream` | `bool` | `False` | Whether to use streaming result |
| `result_class` | `type` | `tuple` | Result type |

### Constructor

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

**Parameter Description**:

- `url` (str, optional): MySQL connection URL, format: `mysql://user:password@host:port/?charset=utf8mb4`
- `host` (str, optional): MySQL server address
- `port` (int, optional): MySQL server port
- `user` (str, optional): Username
- `password` (str, optional): Password
- `charset` (str, optional): Character set
- `min_pool_size` (int, optional): Minimum connection pool size
- `max_pool_size` (int, optional): Maximum connection pool size
- `pool_recycle` (float, optional): Idle connection recycle time (seconds)
- `connect_timeout` (int, optional): Connection timeout (seconds)
- `auto_commit` (bool, optional): Whether to auto-commit transactions
- `echo_sql_log` (bool, optional): Whether to print SQL logs
- `stream` (bool, optional): Whether to use streaming result
- `result_class` (type, optional): Result type

**Examples**:

```python
# Using URL
engine = Engine(url="mysql://root:pass@127.0.0.1:3306/?charset=utf8mb4")

# Using keyword arguments
engine = Engine(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="pass",
    charset="utf8mb4"
)
```

### Methods

#### connect()

Connect to MySQL, establish TCP connection, initialize connection pool.

```python
async def connect(self) -> Engine
```

**Return Value**: Returns `self`, supports chaining

**Example**:

```python
await engine.connect()
```

#### disconnect()

Wait for all connections to be released and properly close MySQL connection.

```python
async def disconnect(self) -> None
```

**Example**:

```python
await engine.disconnect()
```

#### release_connections()

Release all idle connections in the connection pool.

```python
async def release_connections(self) -> None
```

**Example**:

```python
await engine.release_connections()
```

#### execute()

Execute SQL statement and return Result object.

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

**Parameter Description**:

- `query` (str): SQL statement
- `values` (Union[Sequence, dict], optional): Parameters, can be tuple or dict
- `stream` (bool, optional): Whether to stream results, defaults to `self.stream`
- `result_class` (type, optional): Result type, defaults to `self.result_class`
- `commit` (bool, optional): Whether to commit transaction, defaults to `self.auto_commit`

**Return Value**: Returns `Result` object, supports the following usages:

1. `result = await engine.execute(...)`
2. `async with engine.execute(...) as result:`
3. `async for item in engine.execute(...):`

**Examples**:

```python
# Method 1: await
result = await engine.execute("SELECT * FROM users WHERE id = %s", (1,))
data = await result.fetch_one()

# Method 2: context manager
async with engine.execute("SELECT * FROM users") as result:
    data = await result.fetch_all()

# Method 3: direct iteration
async for row in engine.execute("SELECT * FROM users"):
    print(row)
```

#### execute_many()

Batch execute SQL statements and return Result object.

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

**Parameter Description**:

- `query` (str): SQL statement
- `values` (Sequence[Union[Sequence, dict]]): Parameter list, each element can be tuple or dict
- `stream` (bool, optional): Whether to stream results
- `result_class` (type, optional): Result type
- `commit` (bool, optional): Whether to commit transaction

**Return Value**: Returns `Result` object

**Example**:

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

### Attributes

#### status

Returns database connection pool status.

```python
@property
def status(self) -> EngineStatus
```

**Return Value**: `EngineStatus` dictionary, contains the following fields:

- `address` (str): Connection address
- `connected` (bool): Whether connected
- `pool_minsize` (Optional[int]): Connection pool minimum size
- `pool_maxsize` (Optional[int]): Connection pool maximum size
- `pool_size` (Optional[int]): Connection pool current size
- `pool_free` (Optional[int]): Number of idle connections
- `pool_used` (Optional[int]): Number of connections in use

**Example**:

```python
status = engine.status
print(f"Connection status: {status['connected']}")
print(f"Pool size: {status['pool_size']}")
```

#### is_connected

Whether the database is connected.

```python
@property
def is_connected(self) -> bool
```

**Return Value**: `bool`, returns `True` if connected, otherwise `False`

**Example**:

```python
if engine.is_connected:
    print("Connected")
```

#### pool

Get connection pool object (internal use).

```python
@property
def pool(self) -> Pool
```

**Return Value**: `aiomysql.Pool` object

**Note**: This attribute is for internal use only, will raise `ConnectionError` if not connected

#### url

Connection URL (read-only).

```python
url: Final[str]
```

**Example**:

```python
print(engine.url)  # mysql://127.0.0.1:3306/
```

### Special Methods

#### __aenter__() / __aexit__()

Support for `async with` syntax.

```python
async def __aenter__(self) -> Engine
async def __aexit__(self, exc_type, exc_value, exc_tb) -> None
```

**Example**:

```python
async with engine:
    result = await engine.execute("SELECT * FROM users")
    data = await result.fetch_all()
```

#### __await__()

Support for `await engine` syntax.

```python
def __await__(self) -> Generator[Any, None, Engine]
```

**Example**:

```python
await engine  # Equivalent to await engine.connect()
```

#### __call__()

Support for `await engine()` syntax.

```python
async def __call__(self) -> Engine
```

**Example**:

```python
await engine()  # Equivalent to await engine.connect()
```

## AsMysql Class

`AsMysql` is the base class for business logic development, used to encapsulate business methods.

### Class Definition

```python
class AsMysql:
    """Class for writing MySQL business logic"""
```

### Constructor

```python
def __init__(self, engine: Engine) -> None
```

**Parameter Description**:

- `engine` (Engine): `Engine` instance

**Example**:

```python
engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")
await engine.connect()

class UserService(AsMysql):
    pass

service = UserService(engine)
```

### Attributes

#### client

Access `Engine` instance.

```python
@property
def client(self) -> Engine
```

**Return Value**: `Engine` instance

**Example**:

```python
class UserService(AsMysql):
    async def get_users(self):
        result = await self.client.execute("SELECT * FROM users")
        return await result.fetch_all()
```

## Result Class

`Result` is the encapsulation class for SQL execution results, providing data retrieval and error handling functionality.

### Class Definition

```python
class Result(Generic[T]):
    """SQL execution result class"""
```

### Constructor

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

**Parameter Description** (internal use, usually no need to construct directly):

- `pool` (Pool): Connection pool object
- `query` (str): SQL statement
- `values` (Union[Sequence, dict], optional): Parameters
- `execute_many` (bool): Whether batch execution
- `stream` (bool): Whether streaming result
- `commit` (bool): Whether to commit transaction
- `result_class` (type): Result type

### Methods

#### fetch_one()

Get a single record.

```python
async def fetch_one(self, close: bool = None) -> Optional[T]
```

**Parameter Description**:

- `close` (bool, optional): Whether to automatically close cursor connection. If set to `False`, must manually call `Result.close()` to release connection

**Return Value**: Returns a single record, returns `None` if no data

**Example**:

```python
result = await engine.execute("SELECT * FROM users WHERE id = %s", (1,))
user = await result.fetch_one()
if user:
    print(user)
```

#### fetch_many()

Get multiple records.

```python
async def fetch_many(self, size: int = None, close: bool = None) -> list[T]
```

**Parameter Description**:

- `size` (int, optional): Number of records to fetch, defaults to all available records
- `close` (bool, optional): Whether to automatically close cursor connection

**Return Value**: Returns list of records

**Example**:

```python
result = await engine.execute("SELECT * FROM users")
users = await result.fetch_many(10)  # Get 10 records
```

#### fetch_all()

Get all records.

```python
async def fetch_all(self) -> list[T]
```

**Return Value**: Returns list of all records

**Note**: This method will automatically close cursor connection

**Example**:

```python
result = await engine.execute("SELECT * FROM users")
all_users = await result.fetch_all()
```

#### iterate()

Async generator, iterate through all records.

```python
async def iterate(self) -> AsyncGenerator[T, None]
```

**Return Value**: Async generator, returns records row by row

**Note**: This method will automatically close cursor connection

**Example**:

```python
result = await engine.execute("SELECT * FROM users")
async for user in result.iterate():
    print(user)
```

#### close()

Close cursor and release connection.

```python
async def close(self) -> None
```

**Example**:

```python
result = await engine.execute("SELECT * FROM users")
data = await result.fetch_one(close=False)
# ... other operations
await result.close()  # Manual close
```

### Attributes

#### error

Error exception object.

```python
@property
def error(self) -> Optional[MySQLError]
```

**Return Value**: `MySQLError` exception object, returns `None` if no error

**Example**:

```python
result = await engine.execute("SELECT * FROM invalid_table")
if result.error:
    print(f"Error: {result.error}")
```

#### error_no

Error code.

```python
@property
def error_no(self) -> int
```

**Return Value**: Error code (integer), returns `0` if no error

**Example**:

```python
if result.error:
    print(f"Error code: {result.error_no}")
```

#### error_msg

Error message.

```python
@property
def error_msg(self) -> str
```

**Return Value**: Error message (string), returns empty string if no error

**Example**:

```python
if result.error:
    print(f"Error message: {result.error_msg}")
```

#### row_count

Number of affected rows.

```python
@property
def row_count(self) -> Optional[int]
```

**Return Value**:
- Number of affected rows (integer)
- Returns `None` if error occurs
- Returns `None` if using streaming query (`stream=True`)

**Example**:

```python
result = await engine.execute("INSERT INTO users (name) VALUES (%s)", ("张三",))
print(f"Inserted {result.row_count} records")
```

#### last_rowid

ID of the most recently inserted record.

```python
@property
def last_rowid(self) -> Optional[int]
```

**Return Value**:
- ID of the most recently inserted record (integer)
- Returns `None` if no data inserted or error occurs

**Example**:

```python
result = await engine.execute("INSERT INTO users (name) VALUES (%s)", ("张三",))
print(f"Newly inserted ID: {result.last_rowid}")
```

#### row_number

Current cursor position.

```python
@property
def row_number(self) -> Optional[int]
```

**Return Value**:
- Current cursor row index in result set (0-based)
- Returns `None` if index cannot be determined or error occurs

**Example**:

```python
result = await engine.execute("SELECT * FROM users")
while True:
    row = await result.fetch_one(close=False)
    if not row:
        break
    print(f"Current position: {result.row_number}")
```

### Special Methods

#### __aenter__() / __aexit__()

Support for `async with` syntax.

```python
async def __aenter__(self) -> Result[T]
async def __aexit__(self, exc_type, exc_value, exc_tb) -> None
```

**Example**:

```python
async with engine.execute("SELECT * FROM users") as result:
    data = await result.fetch_all()
```

#### __aiter__() / __anext__()

Support for `async for` syntax.

```python
def __aiter__(self) -> Result[T]
async def __anext__(self) -> T
```

**Example**:

```python
result = await engine.execute("SELECT * FROM users")
async for user in result:
    print(user)
```

#### __await__()

Support for `await result` syntax.

```python
def __await__(self) -> Generator[Any, None, Result[T]]
```

**Example**:

```python
result = await engine.execute("SELECT * FROM users")
# Equivalent to executing SQL query
```

#### __call__()

Support for `await result()` syntax.

```python
async def __call__(self) -> Result[T]
```

**Example**:

```python
result = engine.execute("SELECT * FROM users")
await result()  # Execute query
data = await result.fetch_all()
```

## Type Definitions

### EngineStatus

Connection engine status type.

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

### Type Aliases

```python
AsyncEngine = Engine
AsyncResult = Result
```

These type aliases are used for backward compatibility or type hints.

## Import Methods

```python
# Method 1: Import from main module
from asmysql import Engine, AsMysql, Result

# Method 2: Import from v2 submodule
from asmysql.v2 import Engine, AsMysql, Result

# Method 3: Use type aliases
from asmysql import AsyncEngine, AsyncResult
```

