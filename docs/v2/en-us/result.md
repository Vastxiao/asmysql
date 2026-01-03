# Result Processing

## Retrieve Result Data

### fetch_one() - Get Single Record

```python
result = await engine.execute("SELECT * FROM users WHERE id = %s", (1,))
user = await result.fetch_one()
if user:
    print(user)
```

### fetch_many() - Get Multiple Records

```python
result = await engine.execute("SELECT * FROM users")
users = await result.fetch_many(10)  # Get 10 records
for user in users:
    print(user)
```

### fetch_all() - Get All Records

```python
result = await engine.execute("SELECT * FROM users")
all_users = await result.fetch_all()
print(f"Total {len(all_users)} records")
```

### iterate() - Async Iterator

```python
result = await engine.execute("SELECT * FROM users")
async for user in result.iterate():
    print(user)
```

### Direct Iteration of Result

```python
# Method 1: Direct iteration of execute result
async for user in engine.execute("SELECT * FROM users"):
    print(user)

# Method 2: await then iterate
result = await engine.execute("SELECT * FROM users")
async for user in result:
    print(user)
```

## Result Types

### Default tuple Type

```python
result = await engine.execute("SELECT id, name, email FROM users")
user = await result.fetch_one()
# user is tuple: (1, "张三", "zhangsan@example.com")
```

### dict Type

```python
result = await engine.execute(
    "SELECT id, name, email FROM users",
    result_class=dict
)
user = await result.fetch_one()
# user is dict: {"id": 1, "name": "张三", "email": "zhangsan@example.com"}
```

### Custom Model Type

```python
from pydantic import BaseModel
from asmysql import Engine

class User(BaseModel):
    id: int
    name: str
    email: str

engine = Engine(url="mysql://root:pass@127.0.0.1:3306/")
await engine.connect()

result = await engine.execute(
    "SELECT id, name, email FROM users",
    result_class=User
)
user = await result.fetch_one()
# user is User instance
print(user.name)  # Use attribute access
```

## Error Handling

### Check Error

```python
result = await engine.execute("SELECT * FROM non_existent_table")
if result.error:
    print(f"Error code: {result.error_no}")
    print(f"Error message: {result.error_msg}")
    print(f"Error object: {result.error}")
else:
    data = await result.fetch_all()
```

### Error Attributes

- `result.error`: Error exception object (`MySQLError` or `None`)
- `result.error_no`: Error code (integer, 0 when no error)
- `result.error_msg`: Error message (string, empty string when no error)

## Execution Statistics

```python
result = await engine.execute("INSERT INTO users (name) VALUES (%s)", ("张三",))

# Affected rows
print(f"Affected rows: {result.row_count}")

# Last inserted ID (only for INSERT statements)
print(f"Last inserted ID: {result.last_rowid}")

# Current cursor position
print(f"Cursor position: {result.row_number}")
```

**Note**:
- `row_count` returns `None` when using streaming query (`stream=True`)
- `row_count` returns `None` when an error occurs
- `last_rowid` is only valid for INSERT statements

