# asmysql v2 使用示例

本文档提供 asmysql v2 版本的详细使用示例。

## 导航

- [基础示例](#basic-examples)
- [连接管理](#connection-management)
- [查询操作](#query-operations)
- [插入操作](#insert-operations)
- [更新操作](#update-operations)
- [删除操作](#delete-operations)
- [事务处理](#transaction-processing)
- [流式查询](#streaming-queries)
- [批量操作](#batch-operations)
- [自定义模型](#custom-models)
- [错误处理](#error-handling)
- [业务逻辑封装](#business-logic-encapsulation)
- [完整应用示例](#complete-application-examples)

## 基础示例 {#basic-examples}

### 最简单的查询

```python
import asyncio
from asmysql import Engine

async def main():
    # 创建引擎
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    
    # 连接
    await engine.connect()
    
    # 执行查询
    result = await engine.execute("SELECT 1 as value")
    data = await result.fetch_one()
    print(data)  # (1,)
    
    # 断开连接
    await engine.disconnect()

asyncio.run(main())
```

### 使用上下文管理器

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

## 连接管理 {#connection-management}

### 检查连接状态

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    
    print(f"连接前: {engine.is_connected}")  # False
    
    await engine.connect()
    print(f"连接后: {engine.is_connected}")  # True
    
    # 查看连接池状态
    status = engine.status
    print(f"连接地址: {status['address']}")
    print(f"连接池大小: {status['pool_size']}")
    print(f"空闲连接: {status['pool_free']}")
    print(f"使用中连接: {status['pool_used']}")
    
    await engine.disconnect()

asyncio.run(main())
```

### 连接池配置

```python
from asmysql import Engine

# 配置连接池
engine = Engine(
    url="mysql://root:pass@127.0.0.1:3306/test_db",
    min_pool_size=5,      # 最小连接数
    max_pool_size=50,     # 最大连接数
    pool_recycle=3600,    # 1 小时回收空闲连接
    connect_timeout=10    # 连接超时 10 秒
)
```

## 查询操作 {#query-operations}

### 单条记录查询

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    # 使用 tuple 类型（默认）
    result = await engine.execute(
        "SELECT id, name, email FROM users WHERE id = %s",
        (1,)
    )
    user = await result.fetch_one()
    if user:
        print(f"ID: {user[0]}, 姓名: {user[1]}, 邮箱: {user[2]}")
    
    # 使用 dict 类型
    result = await engine.execute(
        "SELECT id, name, email FROM users WHERE id = %s",
        (1,),
        result_class=dict
    )
    user = await result.fetch_one()
    if user:
        print(f"ID: {user['id']}, 姓名: {user['name']}, 邮箱: {user['email']}")
    
    await engine.disconnect()

asyncio.run(main())
```

### 多条记录查询

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    # 获取所有记录
    result = await engine.execute("SELECT * FROM users")
    all_users = await result.fetch_all()
    print(f"共 {len(all_users)} 条记录")
    
    # 获取指定数量的记录
    result = await engine.execute("SELECT * FROM users")
    users = await result.fetch_many(10)  # 获取 10 条
    print(f"获取了 {len(users)} 条记录")
    
    await engine.disconnect()

asyncio.run(main())
```

### 使用字典参数

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    # 使用字典参数
    result = await engine.execute(
        "SELECT * FROM users WHERE name = %(name)s AND age > %(age)s",
        {"name": "张三", "age": 18}
    )
    users = await result.fetch_all()
    
    await engine.disconnect()

asyncio.run(main())
```

### 使用迭代器

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    # 方式一：使用 iterate() 方法
    result = await engine.execute("SELECT * FROM users")
    async for user in result.iterate():
        print(user)
    
    # 方式二：直接迭代 result
    result = await engine.execute("SELECT * FROM users")
    async for user in result:
        print(user)
    
    # 方式三：直接迭代 execute 返回的结果
    async for user in engine.execute("SELECT * FROM users"):
        print(user)
    
    await engine.disconnect()

asyncio.run(main())
```

## 插入操作 {#insert-operations}

### 单条插入

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    # 插入数据
    result = await engine.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s)",
        ("张三", "zhangsan@example.com")
    )
    
    if result.error:
        print(f"插入失败: {result.error_msg}")
    else:
        print(f"插入成功，受影响行数: {result.row_count}")
        print(f"新插入的 ID: {result.last_rowid}")
    
    await engine.disconnect()

asyncio.run(main())
```

### 获取插入的 ID

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
        print(f"新用户的 ID: {new_id}")
    
    await engine.disconnect()

asyncio.run(main())
```

## 更新操作 {#update-operations}

### 更新单条记录

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
        print(f"更新失败: {result.error_msg}")
    else:
        print(f"更新成功，受影响行数: {result.row_count}")
    
    await engine.disconnect()

asyncio.run(main())
```

### 批量更新

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    # 使用 execute_many 批量更新
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
        print(f"批量更新成功，受影响行数: {result.row_count}")
    
    await engine.disconnect()

asyncio.run(main())
```

## 删除操作 {#delete-operations}

### 删除记录

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
        print(f"删除失败: {result.error_msg}")
    else:
        print(f"删除成功，受影响行数: {result.row_count}")
    
    await engine.disconnect()

asyncio.run(main())
```

## 事务处理 {#transaction-processing}

### 基本事务

```python
import asyncio
from asmysql import Engine

async def main():
    # 关闭自动提交
    engine = Engine(
        url="mysql://root:pass@127.0.0.1:3306/test_db",
        auto_commit=False
    )
    await engine.connect()
    
    try:
        # 插入用户
        result1 = await engine.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            ("张三", "zhangsan@example.com"),
            commit=False
        )
        if result1.error:
            raise Exception(result1.error_msg)
        
        user_id = result1.last_rowid
        
        # 插入用户详情
        result2 = await engine.execute(
            "INSERT INTO user_profiles (user_id, bio) VALUES (%s, %s)",
            (user_id, "这是张三的个人简介"),
            commit=False
        )
        if result2.error:
            raise Exception(result2.error_msg)
        
        # 手动提交（需要访问连接对象）
        # 注意：v2 版本的事务管理需要手动控制
        # 这里简化示例，实际使用时需要更精细的控制
        
    except Exception as e:
        print(f"事务失败: {e}")
        # 回滚操作需要手动处理
    
    await engine.disconnect()

asyncio.run(main())
```

## 流式查询 {#streaming-queries}

### 处理大数据集

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    # 启用流式查询
    result = await engine.execute(
        "SELECT * FROM large_table",
        stream=True
    )
    
    count = 0
    async for row in result:
        count += 1
        # 处理每一行数据，不占用内存
        process_row(row)
        
        if count % 1000 == 0:
            print(f"已处理 {count} 条记录")
    
    print(f"总共处理了 {count} 条记录")
    
    await engine.disconnect()

def process_row(row):
    """处理单行数据"""
    pass

asyncio.run(main())
```

### 流式查询与普通查询对比

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    # 普通查询：所有数据加载到内存
    result1 = await engine.execute("SELECT * FROM large_table", stream=False)
    all_data = await result1.fetch_all()  # 可能内存溢出
    print(f"普通查询获取 {len(all_data)} 条记录")
    
    # 流式查询：逐行处理，不占用内存
    result2 = await engine.execute("SELECT * FROM large_table", stream=True)
    count = 0
    async for row in result2:
        count += 1
    print(f"流式查询处理 {count} 条记录")
    
    await engine.disconnect()

asyncio.run(main())
```

## 批量操作 {#batch-operations}

### 批量插入

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    # 准备批量数据
    users = [
        ("张三", "zhangsan@example.com"),
        ("李四", "lisi@example.com"),
        ("王五", "wangwu@example.com"),
        ("赵六", "zhaoliu@example.com")
    ]
    
    # 批量插入
    result = await engine.execute_many(
        "INSERT INTO users (name, email) VALUES (%s, %s)",
        users
    )
    
    if result.error:
        print(f"批量插入失败: {result.error_msg}")
    else:
        print(f"批量插入成功，插入了 {result.row_count} 条记录")
    
    await engine.disconnect()

asyncio.run(main())
```

### 使用字典批量插入

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    # 使用字典格式的批量数据
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
        print(f"批量插入成功，插入了 {result.row_count} 条记录")
    
    await engine.disconnect()

asyncio.run(main())
```

## 自定义模型 {#custom-models}

### 使用 Pydantic 模型

```python
import asyncio
from pydantic import BaseModel
from asmysql import Engine

# 定义用户模型
class User(BaseModel):
    id: int
    name: str
    email: str
    age: int = 0

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    # 查询并使用自定义模型
    result = await engine.execute(
        "SELECT id, name, email, age FROM users WHERE id = %s",
        (1,),
        result_class=User
    )
    
    user = await result.fetch_one()
    if user:
        print(f"用户: {user.name}, 邮箱: {user.email}, 年龄: {user.age}")
        # 可以使用模型的所有功能
        print(user.model_dump())
    
    # 批量查询
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

### 使用普通类

```python
import asyncio
from asmysql import Engine

# 定义普通类
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
        print(user)  # 自动转换为 User 实例
    
    await engine.disconnect()

asyncio.run(main())
```

## 错误处理 {#error-handling}

### 基本错误处理

```python
import asyncio
from asmysql import Engine

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    result = await engine.execute("SELECT * FROM non_existent_table")
    
    if result.error:
        print(f"错误码: {result.error_no}")
        print(f"错误信息: {result.error_msg}")
        print(f"错误对象: {result.error}")
    else:
        data = await result.fetch_all()
        print(f"查询成功，获取 {len(data)} 条记录")
    
    await engine.disconnect()

asyncio.run(main())
```

### 错误处理装饰器

```python
import asyncio
from functools import wraps
from asmysql import Engine

def handle_db_errors(func):
    """数据库错误处理装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            print(f"数据库操作失败: {e}")
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
        raise Exception(f"查询失败: {result.error_msg}")
    return await result.fetch_one()

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    user = await get_user(engine, 1)
    if user:
        print(f"用户: {user['name']}")
    
    await engine.disconnect()

asyncio.run(main())
```

## 业务逻辑封装 {#business-logic-encapsulation}

### 用户服务类

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
    """用户服务类"""
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据 ID 获取用户"""
        result = await self.client.execute(
            "SELECT id, name, email, age FROM users WHERE id = %s",
            (user_id,),
            result_class=User
        )
        if result.error:
            return None
        return await result.fetch_one()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await self.client.execute(
            "SELECT id, name, email, age FROM users WHERE email = %s",
            (email,),
            result_class=User
        )
        if result.error:
            return None
        return await result.fetch_one()
    
    async def list_users(self, limit: int = 100) -> List[User]:
        """获取用户列表"""
        result = await self.client.execute(
            "SELECT id, name, email, age FROM users LIMIT %s",
            (limit,),
            result_class=User
        )
        if result.error:
            return []
        return await result.fetch_all()
    
    async def create_user(self, name: str, email: str, age: int = 0) -> Optional[int]:
        """创建用户"""
        result = await self.client.execute(
            "INSERT INTO users (name, email, age) VALUES (%s, %s, %s)",
            (name, email, age)
        )
        if result.error:
            return None
        return result.last_rowid
    
    async def update_user(self, user_id: int, name: str = None, email: str = None, age: int = None) -> bool:
        """更新用户"""
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
        """删除用户"""
        result = await self.client.execute(
            "DELETE FROM users WHERE id = %s",
            (user_id,)
        )
        return result.error is None

async def main():
    engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")
    await engine.connect()
    
    user_service = UserService(engine)
    
    # 创建用户
    user_id = await user_service.create_user("张三", "zhangsan@example.com", 25)
    print(f"创建用户，ID: {user_id}")
    
    # 获取用户
    user = await user_service.get_user_by_id(user_id)
    if user:
        print(f"用户: {user.name}, 邮箱: {user.email}, 年龄: {user.age}")
    
    # 更新用户
    success = await user_service.update_user(user_id, age=26)
    print(f"更新用户: {success}")
    
    # 获取用户列表
    users = await user_service.list_users(10)
    print(f"用户列表，共 {len(users)} 条")
    
    await engine.disconnect()

asyncio.run(main())
```

## 完整应用示例 {#complete-application-examples}

### Web 应用示例（FastAPI）

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from asmysql import Engine, AsMysql
from contextlib import asynccontextmanager

# 全局引擎
engine = Engine(url="mysql://root:pass@127.0.0.1:3306/test_db")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时连接
    await engine.connect()
    yield
    # 关闭时断开
    await engine.disconnect()

app = FastAPI(lifespan=lifespan)

# 数据模型
class UserCreate(BaseModel):
    name: str
    email: str
    age: int = 0

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int

# 服务类
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

# API 路由
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

### 命令行工具示例

```python
import asyncio
import argparse
from asmysql import Engine, AsMysql

class UserCLI(AsMysql):
    async def list_users(self):
        """列出所有用户"""
        result = await self.client.execute(
            "SELECT id, name, email FROM users",
            result_class=dict
        )
        if result.error:
            print(f"错误: {result.error_msg}")
            return
        
        users = await result.fetch_all()
        print(f"共 {len(users)} 个用户:")
        for user in users:
            print(f"  ID: {user['id']}, 姓名: {user['name']}, 邮箱: {user['email']}")
    
    async def add_user(self, name: str, email: str):
        """添加用户"""
        result = await self.client.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            (name, email)
        )
        if result.error:
            print(f"添加失败: {result.error_msg}")
        else:
            print(f"添加成功，ID: {result.last_rowid}")

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
    
    # 创建引擎
    engine = Engine(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password
    )
    
    await engine.connect()
    
    # 选择数据库
    await engine.execute(f"USE {args.database}")
    
    # 创建 CLI 实例
    cli = UserCLI(engine)
    
    # 执行命令
    if args.command == "list":
        await cli.list_users()
    elif args.command == "add":
        await cli.add_user(args.name, args.email)
    
    await engine.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

这些示例涵盖了 asmysql v2 版本的主要使用场景，可以根据实际需求进行修改和扩展。

