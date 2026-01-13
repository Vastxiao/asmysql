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
result = await engine.execute("SELECT * FROM users")
# Forgot await engine.disconnect()
```

## 2. About `close` Parameter

The `fetch_one()` and `fetch_many()` methods provide a `close` parameter to control whether to automatically close the cursor connection:

### ✅ Recommended: Use Context Manager (Automatic Connection Management)

When using `async with`, the connection will be automatically closed when exiting the context, no manual management needed:

```python
async with engine.execute("SELECT * FROM users") as result:
    data = await result.fetch_one()  # close parameter will be ignored, connection managed by context manager
    # Automatically close connection on exit
```

### ✅ Recommended: Use `async for` (Automatic Connection Management)

When using `async for`, the connection will be automatically closed after iteration completes:

```python
async for item in engine.execute("SELECT * FROM users"):
    print(item)
    # Automatically close connection after iteration completes
```

### ⚠️ Note: Manual Control of `close` Parameter

If you need to manually control connection closing in `fetch_one()` or `fetch_many()`, note:

```python
# Default behavior: automatically close connection (recommended)
result = await engine.execute("SELECT * FROM users")
data = await result.fetch_one()  # Default close=True, automatically close connection

# Manual control: do not auto-close (need manual release)
result = await engine.execute("SELECT * FROM users")
data1 = await result.fetch_one(close=False)  # Do not close connection
data2 = await result.fetch_one(close=False)  # Continue using same connection
await result.close()  # ⚠️ Must manually close, otherwise connection pool may have issues
```

**Important Notes**:
- If setting `close=False`, **must** call `result.close()` to release connection after completion
- Otherwise the connection will not be returned to the pool, which may cause connection pool exhaustion
- When using context manager or `async for`, the `close` parameter will be ignored, connection is automatically managed by the framework

## 3. Error Handling

### ✅ Recommended: Check Errors

```python
result = await engine.execute("SELECT * FROM users")
if result.error:
    logger.error(f"Query failed: {result.error_msg}")
    return []
return await result.fetch_all()
```

### ❌ Not Recommended: Ignore Errors

```python
result = await engine.execute("SELECT * FROM users")
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
data = await engine.execute("SELECT * FROM large_table")
all_data = await data.fetch_all()  # May cause memory overflow
```

## 5. Parameterized Queries

### ✅ Recommended: Use Parameterized Queries to Prevent SQL Injection

```python
result = await engine.execute(
    "SELECT * FROM users WHERE name = %s",
    (user_name,)
)
```

### ❌ Not Recommended: String Concatenation

```python
result = await engine.execute(
    f"SELECT * FROM users WHERE name = '{user_name}'"
)
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

## Related Documentation

- [Connection Management](connection.md) - Learn detailed connection configuration
- [Query Operations](query.md) - Learn query best practices

