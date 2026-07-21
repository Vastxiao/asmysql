# Best Practices

## 1. For Simple MySQL Connection Scenarios, Use Context Management

### ✅ Recommended: Use Context Manager

```python
# Use context manager to automatically manage connections
async with engine:
    # Execute SQL statement using context manager
    async with engine.execute("select user,host from mysql.user") as result:
        async for item in result.iterate():
            print(item)
    # Automatically disconnect MySQL connection on exit
```

### ❌ Not Recommended: Forget to Disconnect

```python
await engine.connect()
async with engine.execute("SELECT * FROM users") as result:
    pass
# Forgot await engine.disconnect()
```

## 2. About Connection Resource Management

`Result` objects returned by `execute()` / `execute_many()` must be used via `async with` or `async for` to ensure proper connection release:

### ✅ Recommended: Use Context Manager (Automatic Connection Management)

When using `async with`, the connection will be automatically closed when exiting the context:

```python
async with engine.execute("SELECT * FROM users") as result:
    data = await result.fetch_one()
    # Automatically close connection on exit
```

### ✅ Recommended: Use `async for` (Automatic Connection Management)

When using `async for`, the connection will be automatically closed after iteration completes:

```python
async for item in engine.execute("SELECT * FROM users"):
    print(item)
    # Automatically close connection after iteration completes
```

### ⚠️ Note: Must Use async with or async for

`execute()` returns a `Result` object (not a coroutine) and cannot be `await`ed. It must be used via `async with` or `async for`:

```python
# ✅ Correct: Use async with
async with engine.execute("SELECT * FROM users") as result:
    data = await result.fetch_one()

# ✅ Correct: Use async for
async for item in engine.execute("SELECT * FROM users"):
    print(item)

# ❌ Wrong: Cannot await (execute is not a coroutine)
# result = await engine.execute("SELECT * FROM users")
```

**Important Notes**:
- `Result` objects must be used via `async with` or `async for`, otherwise the connection will not be returned to the pool
- Failing to properly close `Result` will cause `ResourceWarning` and connection leaks
- When using context manager or `async for`, connections are automatically managed by the framework

## 3. Error Handling

### ✅ Recommended: Check Errors

```python
async with engine.execute("SELECT * FROM users") as result:
    if result.error:
        logger.error(f"Query failed: {result.error_msg}")
        return []
    return await result.fetch_all()
```

### ❌ Not Recommended: Ignore Errors

```python
async with engine.execute("SELECT * FROM users") as result:
    data = await result.fetch_all()  # If error occurs, data may be empty list
```

## 4. Large Dataset Processing

### ✅ Recommended: Use Streaming Query

```python
async for row in engine.execute("SELECT * FROM large_table", stream=True):
    process(row)
```

### ❌ Not Recommended: Load All Data at Once

```python
async with engine.execute("SELECT * FROM large_table") as result:
    all_data = await result.fetch_all()  # May cause memory overflow
```

## 5. Parameterized Queries

### ✅ Recommended: Use Parameterized Queries to Prevent SQL Injection

```python
async with engine.execute(
    "SELECT * FROM users WHERE name = %s",
    (user_name,)
) as result:
    users = await result.fetch_all()
```

### ❌ Not Recommended: String Concatenation

```python
async with engine.execute(
    f"SELECT * FROM users WHERE name = '{user_name}'"
) as result:
    users = await result.fetch_all()
```

## 6. Connection Pool Configuration

### ✅ Recommended: Configure Connection Pool Based on Application Load

```python
engine = Engine(
    url="mysql://root:pass@127.0.0.1:3306/",
    min_pool_size=5,   # Maintain minimum connections
    max_pool_size=50,  # Set maximum based on concurrency
    pool_recycle=3600  # Recycle idle connections after 1 hour
)
```

### ❌ Not Recommended: Use Default Values (May Not Be Suitable for Production)

```python
engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")
```
