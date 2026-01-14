# Query Operations

## Basic Query

### Method 1: Using await

```python
from asmysql import Engine

engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")
await engine.connect()

result = await engine.execute("SELECT * FROM users WHERE id = %s", (1,))
data = await result.fetch_one()
```

### Method 2: Using Context Manager

```python
from asmysql import Engine

engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")
await engine.connect()

async with engine.execute("SELECT * FROM users") as result:
    data = await result.fetch_all()
```

### Method 3: Direct Iteration

```python
from asmysql import Engine

engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")
await engine.connect()

async for row in engine.execute("SELECT * FROM users"):
    print(row)
```

## Parameterized Query

### Using Tuple Parameters

```python
result = await engine.execute(
    "SELECT * FROM users WHERE name = %s AND age > %s",
    ("张三", 18)
)
```

### Using Dictionary Parameters

```python
result = await engine.execute(
    "SELECT * FROM users WHERE name = %(name)s AND age > %(age)s",
    {"name": "张三", "age": 18}
)
```

## Batch Execution

```python
# Batch insert
users = [
    ("张三", "zhangsan@example.com"),
    ("李四", "lisi@example.com"),
    ("王五", "wangwu@example.com")
]
result = await engine.execute_many(
    "INSERT INTO users (name, email) VALUES (%s, %s)",
    users
)
print(f"Inserted {result.row_count} records")
```

## Streaming Query

Streaming queries are suitable for large datasets and do not load all data into memory:

```python
# Enable streaming query
result = await engine.execute(
    "SELECT * FROM large_table",
    stream=True
)

# Stream iteration
async for row in result:
    process(row)  # Process row by row without memory consumption
```

## Related Documentation

- [Result Processing](result.md) - Learn how to retrieve and process query results
- [Transaction Control](transaction.md) - Learn about transaction management

