# FAQ

## Q: How to check connection pool status?

A: Use the `engine.status` attribute:

```python
status = engine.status
print(status)
```

## Q: What's the difference between streaming query and regular query?

A:
- **Regular Query**: Loads all results into memory, suitable for small datasets
- **Streaming Query**: Returns results row by row, does not consume memory, suitable for large datasets

## Q: How to customize result type?

A: Use the `result_class` parameter, supports `tuple`, `dict`, or custom model classes:

```python
async with engine.execute(
    "SELECT * FROM users",
    result_class=dict  # or custom model class
) as result:
    users = await result.fetch_all()
```

## Q: How to handle transactions?

A: v2 uses an SQL statement type-based auto-commit mechanism:

```python
engine = Engine(url="...")
await engine.connect()

# Write operations (INSERT/UPDATE/DELETE etc.) are auto-committed
# Read operations (SELECT) do not trigger commits
```

## Q: How to get error information?

A: Through `result.error`, `result.error_no`, and `result.error_msg` attributes:

```python
async with engine.execute("SELECT * FROM invalid_table") as result:
    if result.error:
        print(f"Error code: {result.error_no}")
        print(f"Error message: {result.error_msg}")
```

## Q: How to batch insert data?

A: Use the `execute_many()` method:

```python
data = [("张三", "zhangsan@example.com"), ("李四", "lisi@example.com")]
async with engine.execute_many(
    "INSERT INTO users (name, email) VALUES (%s, %s)",
    data
) as result:
    print(f"Inserted {result.row_count} records")
```

## Q: How to share Engine instance across different modules?

A: You can create an Engine instance at application startup, then share it through dependency injection or global variables:

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

## Q: How to set connection pool size?

A: Set based on application concurrency and database server performance:

- Low concurrency applications: `min_pool_size=2, max_pool_size=10`
- Medium concurrency: `min_pool_size=5, max_pool_size=50`
- High concurrency applications: `min_pool_size=10, max_pool_size=100+`

## Q: How to handle connection timeout?

A: You can set connection timeout through the `connect_timeout` parameter:

```python
engine = Engine(
    url="mysql://...",
    connect_timeout=10  # 10 seconds timeout
)
```
