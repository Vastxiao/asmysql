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
result = await engine.execute(
    "SELECT * FROM users",
    result_class=dict  # or custom model class
)
```

## Q: How to handle transactions?

A: Set `auto_commit=False` and manage manually:

```python
engine = Engine(url="...", auto_commit=False)
await engine.connect()

# Note: Transaction management in v2 requires manual connection control
```

## Q: How to get error information?

A: Through `result.error`, `result.error_no`, and `result.error_msg` attributes:

```python
result = await engine.execute("SELECT * FROM invalid_table")
if result.error:
    print(f"Error code: {result.error_no}")
    print(f"Error message: {result.error_msg}")
```

## Q: How to batch insert data?

A: Use the `execute_many()` method:

```python
data = [("张三", "zhangsan@example.com"), ("李四", "lisi@example.com")]
result = await engine.execute_many(
    "INSERT INTO users (name, email) VALUES (%s, %s)",
    data
)
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

## Related Documentation

- [Connection Management](connection.md) - Learn more about connection configuration
- [Best Practices](best-practices.md) - View recommended usage patterns

