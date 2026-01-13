# asmysql v2 Usage Examples

This document provides detailed usage examples for asmysql v2 version.

## Table of Contents

- [Basic Examples](#基础示例)
- [Connection Management](#连接管理)
- [Query Operations](#查询操作)
- [Insert Operations](#插入操作)
- [Update Operations](#更新操作)
- [Delete Operations](#删除操作)
- [Transaction Processing](#事务处理)
- [Streaming Queries](#流式查询)
- [Batch Operations](#批量操作)
- [Custom Models](#自定义模型)
- [Error Handling](#错误处理)
- [Business Logic Encapsulation](#业务逻辑封装)
- [Complete Application Examples](#完整应用示例)

## Basic Examples

### Simplest Query

```python
import asyncio
from asmysql import Engine

async def main():
    # Create engine
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    
    # Connect
    await engine.connect()
    
    # Execute query
    result = await engine.execute("SELECT 1 as value")
    data = await result.fetch_one()
    print(data)  # (1,)
    
    # Disconnect
    await engine.disconnect()

asyncio.run(main())
```

### Using Context Manager

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    
    async with engine:
        result = await engine.execute("SELECT 1 as value")
        data = await result.fetch_one()
        print(data)

asyncio.run(main())
```

## Connection Management

### Check Connection Status

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    
    print(f"Before connection: {engine.is_connected}")  # False
    
    await engine.connect()
    print(f"After connection: {engine.is_connected}")  # True
    
    # View connection pool status
    status = engine.status
    print(f"Connection address: {status['address']}")
    print(f"Pool size: {status['pool_size']}")
    print(f"Free connections: {status['pool_free']}")
    print(f"Used connections: {status['pool_used']}")
    
    await engine.disconnect()

asyncio.run(main())
```

### Connection Pool Configuration

```python
from asmysql import Engine

# Configure connection pool
engine = Engine(
    url="mysql://root:pass@127.0.0.1:3306/test_db",
    min_pool_size=5,      # Minimum connections
    max_pool_size=50,     # Maximum connections
    pool_recycle=3600,    # Recycle idle connections after 1 hour
    connect_timeout=10    # Connection timeout 10 seconds
)
```

## Query Operations

### Single Record Query

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    # Using tuple type (default)
    result = await engine.execute(
        "SELECT id, name, email FROM users WHERE id = %s",
        (1,)
    )
    user = await result.fetch_one()
    if user:
        print(f"ID: {user[0]}, Name: {user[1]}, Email: {user[2]}")
    
    # Using dict type
    result = await engine.execute(
        "SELECT id, name, email FROM users WHERE id = %s",
        (1,),
        result_class=dict
    )
    user = await result.fetch_one()
    if user:
        print(f"ID: {user['id']}, Name: {user['name']}, Email: {user['email']}")
    
    await engine.disconnect()

asyncio.run(main())
```

### Multiple Records Query

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    # Get all records
    result = await engine.execute("SELECT * FROM users")
    all_users = await result.fetch_all()
    print(f"Total {len(all_users)} records")
    
    # Get specified number of records
    result = await engine.execute("SELECT * FROM users")
    users = await result.fetch_many(10)  # Get 10 records
    print(f"Retrieved {len(users)} records")
    
    await engine.disconnect()

asyncio.run(main())
```

### Using Dictionary Parameters

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    # Using dictionary parameters
    result = await engine.execute(
        "SELECT * FROM users WHERE name = %(name)s AND age > %(age)s",
        {"name": "张三", "age": 18}
    )
    users = await result.fetch_all()
    
    await engine.disconnect()

asyncio.run(main())
```

### Using Iterator

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    # Method 1: Using iterate() method
    result = await engine.execute("SELECT * FROM users")
    async for user in result.iterate():
        print(user)
    
    # Method 2: Direct iteration of result
    result = await engine.execute("SELECT * FROM users")
    async for user in result:
        print(user)
    
    # Method 3: Direct iteration of execute result
    async for user in engine.execute("SELECT * FROM users"):
        print(user)
    
    await engine.disconnect()

asyncio.run(main())
```

## Insert Operations

### Single Insert

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    # Insert data
    result = await engine.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s)",
        ("张三", "zhangsan@example.com")
    )
    
    if result.error:
        print(f"Insert failed: {result.error_msg}")
    else:
        print(f"Insert successful, affected rows: {result.row_count}")
        print(f"Newly inserted ID: {result.last_rowid}")
    
    await engine.disconnect()

asyncio.run(main())
```

### Get Inserted ID

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    result = await engine.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s)",
        ("李四", "lisi@example.com")
    )
    
    if not result.error:
        new_id = result.last_rowid
        print(f"New user ID: {new_id}")
    
    await engine.disconnect()

asyncio.run(main())
```

## Update Operations

### Update Single Record

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    result = await engine.execute(
        "UPDATE users SET email = %s WHERE id = %s",
        ("newemail@example.com", 1)
    )
    
    if result.error:
        print(f"Update failed: {result.error_msg}")
    else:
        print(f"Update successful, affected rows: {result.row_count}")
    
    await engine.disconnect()

asyncio.run(main())
```

### Batch Update

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    # Use execute_many for batch update
    updates = [
        ("email1@example.com", 1),
        ("email2@example.com", 2),
        ("email3@example.com", 3)
    ]
    
    result = await engine.execute_many(
        "UPDATE users SET email = %s WHERE id = %s",
        updates
    )
    
    if not result.error:
        print(f"Batch update successful, affected rows: {result.row_count}")
    
    await engine.disconnect()

asyncio.run(main())
```

## Delete Operations

### Delete Record

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    result = await engine.execute(
        "DELETE FROM users WHERE id = %s",
        (1,)
    )
    
    if result.error:
        print(f"Delete failed: {result.error_msg}")
    else:
        print(f"Delete successful, affected rows: {result.row_count}")
    
    await engine.disconnect()

asyncio.run(main())
```

## Transaction Processing

### Basic Transaction

```python
import asyncio
from asmysql import Engine

async def main():
    # Disable auto commit
    engine = Engine(
        url="mysql://root:pass@127.0.0.1:3306/test_db",
        auto_commit=False
    )
    await engine.connect()
    
    try:
        # Insert user
        result1 = await engine.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            ("张三", "zhangsan@example.com"),
            commit=False
        )
        if result1.error:
            raise Exception(result1.error_msg)
        
        user_id = result1.last_rowid
        
        # Insert user profile
        result2 = await engine.execute(
            "INSERT INTO user_profiles (user_id, bio) VALUES (%s, %s)",
            (user_id, "这是张三的个人简介"),
            commit=False
        )
        if result2.error:
            raise Exception(result2.error_msg)
        
        # Manual commit (need to access connection object)
        # Note: Transaction management in v2 requires manual control
        # This is a simplified example, actual usage requires more fine-grained control
        
    except Exception as e:
        print(f"Transaction failed: {e}")
        # Rollback operations need manual handling
    
    await engine.disconnect()

asyncio.run(main())
```

## Streaming Queries

### Processing Large Datasets

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    # Enable streaming query
    result = await engine.execute(
        "SELECT * FROM large_table",
        stream=True
    )
    
    count = 0
    async for row in result:
        count += 1
        # Process each row of data without memory consumption
        process_row(row)
        
        if count % 1000 == 0:
            print(f"Processed {count} records")
    
    print(f"Total processed {count} records")
    
    await engine.disconnect()

def process_row(row):
    """Process single row of data"""
    pass

asyncio.run(main())
```

### Streaming Query vs Regular Query Comparison

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    # Regular query: All data loaded into memory
    result1 = await engine.execute("SELECT * FROM large_table", stream=False)
    all_data = await result1.fetch_all()  # May cause memory overflow
    print(f"Regular query retrieved {len(all_data)} records")
    
    # Streaming query: Process row by row without memory consumption
    result2 = await engine.execute("SELECT * FROM large_table", stream=True)
    count = 0
    async for row in result2:
        count += 1
    print(f"Streaming query processed {count} records")
    
    await engine.disconnect()

asyncio.run(main())
```

## Batch Operations

### Batch Insert

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    # Prepare batch data
    users = [
        ("张三", "zhangsan@example.com"),
        ("李四", "lisi@example.com"),
        ("王五", "wangwu@example.com"),
        ("赵六", "zhaoliu@example.com")
    ]
    
    # Batch insert
    result = await engine.execute_many(
        "INSERT INTO users (name, email) VALUES (%s, %s)",
        users
    )
    
    if result.error:
        print(f"Batch insert failed: {result.error_msg}")
    else:
        print(f"Batch insert successful, inserted {result.row_count} records")
    
    await engine.disconnect()

asyncio.run(main())
```

### Batch Insert Using Dictionary

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    # Batch data in dictionary format
    users = [
        {"name": "张三", "email": "zhangsan@example.com"},
        {"name": "李四", "email": "lisi@example.com"},
        {"name": "王五", "email": "wangwu@example.com"}
    ]
    
    result = await engine.execute_many(
        "INSERT INTO users (name, email) VALUES (%(name)s, %(email)s)",
        users
    )
    
    if not result.error:
        print(f"Batch insert successful, inserted {result.row_count} records")
    
    await engine.disconnect()

asyncio.run(main())
```

## Custom Models

### Using Pydantic Models

```python
import asyncio
from pydantic import BaseModel
from asmysql import Engine

# Define user model
class User(BaseModel):
    id: int
    name: str
    email: str
    age: int = 0

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    # Query and use custom model
    result = await engine.execute(
        "SELECT id, name, email, age FROM users WHERE id = %s",
        (1,),
        result_class=User
    )
    
    user = await result.fetch_one()
    if user:
        print(f"User: {user.name}, Email: {user.email}, Age: {user.age}")
        # Can use all model features
        print(user.model_dump())
    
    # Batch query
    result = await engine.execute(
        "SELECT id, name, email, age FROM users",
        result_class=User
    )
    
    users = []
    async for user in result.iterate():
        users.append(user)
        print(f"{user.name}: {user.email}")
    
    await engine.disconnect()

asyncio.run(main())
```

### Using Plain Classes

```python
import asyncio
from asmysql import Engine

# Define plain class
class User:
    def __init__(self, id: int, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email
    
    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email})"

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    result = await engine.execute(
        "SELECT id, name, email FROM users",
        result_class=User
    )
    
    async for user in result:
        print(user)  # Automatically converted to User instance
    
    await engine.disconnect()

asyncio.run(main())
```

## Error Handling

### Basic Error Handling

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    result = await engine.execute("SELECT * FROM non_existent_table")
    
    if result.error:
        print(f"Error code: {result.error_no}")
        print(f"Error message: {result.error_msg}")
        print(f"Error object: {result.error}")
    else:
        data = await result.fetch_all()
        print(f"Query successful, retrieved {len(data)} records")
    
    await engine.disconnect()

asyncio.run(main())
```

### Error Handling Decorator

```python
import asyncio
from functools import wraps
from asmysql import Engine

def handle_db_errors(func):
    """Database error handling decorator"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            print(f"Database operation failed: {e}")
            return None
    return wrapper

@handle_db_errors
async def get_user(engine: Engine, user_id: int):
    result = await engine.execute(
        "SELECT * FROM users WHERE id = %s",
        (user_id,),
        result_class=dict
    )
    if result.error:
        raise Exception(f"Query failed: {result.error_msg}")
    return await result.fetch_one()

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    user = await get_user(engine, 1)
    if user:
        print(f"User: {user['name']}")
    
    await engine.disconnect()

asyncio.run(main())
```

## Business Logic Encapsulation

### User Service Class

```python
import asyncio
from typing import Optional, List
from pydantic import BaseModel
from asmysql import Engine, AsMysql

class User(BaseModel):
    id: int
    name: str
    email: str
    age: int = 0

class UserService(AsMysql):
    """User service class"""
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.client.execute(
            "SELECT id, name, email, age FROM users WHERE id = %s",
            (user_id,),
            result_class=User
        )
        if result.error:
            return None
        return await result.fetch_one()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.client.execute(
            "SELECT id, name, email, age FROM users WHERE email = %s",
            (email,),
            result_class=User
        )
        if result.error:
            return None
        return await result.fetch_one()
    
    async def list_users(self, limit: int = 100) -> List[User]:
        """Get user list"""
        result = await self.client.execute(
            "SELECT id, name, email, age FROM users LIMIT %s",
            (limit,),
            result_class=User
        )
        if result.error:
            return []
        return await result.fetch_all()
    
    async def create_user(self, name: str, email: str, age: int = 0) -> Optional[int]:
        """Create user"""
        result = await self.client.execute(
            "INSERT INTO users (name, email, age) VALUES (%s, %s, %s)",
            (name, email, age)
        )
        if result.error:
            return None
        return result.last_rowid
    
    async def update_user(self, user_id: int, name: str = None, email: str = None, age: int = None) -> bool:
        """Update user"""
        updates = []
        values = []
        
        if name is not None:
            updates.append("name = %s")
            values.append(name)
        if email is not None:
            updates.append("email = %s")
            values.append(email)
        if age is not None:
            updates.append("age = %s")
            values.append(age)
        
        if not updates:
            return False
        
        values.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
        
        result = await self.client.execute(query, tuple(values))
        return result.error is None
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        result = await self.client.execute(
            "DELETE FROM users WHERE id = %s",
            (user_id,)
        )
        return result.error is None

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    user_service = UserService(engine)
    
    # Create user
    user_id = await user_service.create_user("张三", "zhangsan@example.com", 25)
    print(f"Created user, ID: {user_id}")
    
    # Get user
    user = await user_service.get_user_by_id(user_id)
    if user:
        print(f"User: {user.name}, Email: {user.email}, Age: {user.age}")
    
    # Update user
    success = await user_service.update_user(user_id, age=26)
    print(f"Update user: {success}")
    
    # Get user list
    users = await user_service.list_users(10)
    print(f"User list, total {len(users)} records")
    
    await engine.disconnect()

asyncio.run(main())
```

## Complete Application Examples

### Web Application Example (FastAPI)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from asmysql import Engine, AsMysql
from contextlib import asynccontextmanager

# Global engine
engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect on startup
    await engine.connect()
    yield
    # Disconnect on shutdown
    await engine.disconnect()

app = FastAPI(lifespan=lifespan)

# Data models
class UserCreate(BaseModel):
    name: str
    email: str
    age: int = 0

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int

# Service class
class UserService(AsMysql):
    async def create_user(self, user_data: UserCreate) -> int:
        result = await self.client.execute(
            "INSERT INTO users (name, email, age) VALUES (%s, %s, %s)",
            (user_data.name, user_data.email, user_data.age)
        )
        if result.error:
            raise HTTPException(status_code=500, detail=result.error_msg)
        return result.last_rowid
    
    async def get_user(self, user_id: int) -> UserResponse:
        result = await self.client.execute(
            "SELECT id, name, email, age FROM users WHERE id = %s",
            (user_id,),
            result_class=UserResponse
        )
        if result.error:
            raise HTTPException(status_code=500, detail=result.error_msg)
        user = await result.fetch_one()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        return user

# API routes
@app.post("/users", response_model=UserResponse)
async def create_user(user_data: UserCreate):
    service = UserService(engine)
    user_id = await service.create_user(user_data)
    return await service.get_user(user_id)

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    service = UserService(engine)
    return await service.get_user(user_id)
```

### Command Line Tool Example

```python
import asyncio
import argparse
from asmysql import Engine, AsMysql

class UserCLI(AsMysql):
    async def list_users(self):
        """List all users"""
        result = await self.client.execute(
            "SELECT id, name, email FROM users",
            result_class=dict
        )
        if result.error:
            print(f"Error: {result.error_msg}")
            return
        
        users = await result.fetch_all()
        print(f"Total {len(users)} users:")
        for user in users:
            print(f"  ID: {user['id']}, Name: {user['name']}, Email: {user['email']}")
    
    async def add_user(self, name: str, email: str):
        """Add user"""
        result = await self.client.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            (name, email)
        )
        if result.error:
            print(f"Add failed: {result.error_msg}")
        else:
            print(f"Add successful, ID: {result.last_rowid}")

async def main():
    parser = argparse.ArgumentParser(description="用户管理工具")
    parser.add_argument("--host", default="127.0.0.1", help="MySQL 主机")
    parser.add_argument("--port", type=int, default=3306, help="MySQL 端口")
    parser.add_argument("--user", default="root", help="MySQL 用户")
    parser.add_argument("--password", default="", help="MySQL 密码")
    parser.add_argument("--database", required=True, help="数据库名")
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    subparsers.add_parser("list", help="列出用户")
    add_parser = subparsers.add_parser("add", help="添加用户")
    add_parser.add_argument("name", help="用户名")
    add_parser.add_argument("email", help="邮箱")
    
    args = parser.parse_args()
    
    # Create engine
    engine = Engine(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password
    )
    
    await engine.connect()
    
    # Select database
    await engine.execute(f"USE {args.database}")
    
    # Create CLI instance
    cli = UserCLI(engine)
    
    # Execute command
    if args.command == "list":
        await cli.list_users()
    elif args.command == "add":
        await cli.add_user(args.name, args.email)
    
    await engine.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

These examples cover the main usage scenarios of asmysql v2 version and can be modified and extended according to actual needs.

