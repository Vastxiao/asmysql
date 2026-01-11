# 快速开始

本指南将帮助你快速上手 asmysql v2。

## 方式一：使用 Engine 类

`Engine` 类是独立的 MySQL 连接引擎，可以直接使用：

```python
import asyncio
from asmysql import Engine

# 创建 MySQL 连接引擎
engine = Engine(url="mysql://root:pass@127.0.0.1:3306/?charset=utf8mb4")

async def main():
    # 连接 MySQL
    await engine.connect()
    
    # 执行 SQL 语句
    async with engine.execute("SELECT user, host FROM mysql.user") as result:
        async for item in result.iterate():
            print(item)
    
    # 断开 MySQL 连接
    await engine.disconnect()

asyncio.run(main())
```

## 方式二：使用 AsMysql 类

`AsMysql` 类用于业务逻辑开发，继承后可直接使用：

```python
import asyncio
from asmysql import Engine, AsMysql

# 创建 MySQL 连接引擎
engine = Engine(url="mysql://root:pass@127.0.0.1:3306/?charset=utf8mb4")

# 编写业务逻辑类
class UserService(AsMysql):
    async def get_all_users(self):
        result = await self.client.execute("SELECT user, host FROM mysql.user")
        if result.error:
            print(f"错误码: {result.error_no}, 错误信息: {result.error_msg}")
        else:
            async for item in result.iterate():
                print(item)

async def main():
    # 连接 MySQL
    await engine.connect()
    
    # 创建业务逻辑实例
    user_service = UserService(engine)
    
    # 执行业务逻辑
    await user_service.get_all_users()
    
    # 断开 MySQL 连接
    await engine.disconnect()

asyncio.run(main())
```

## 下一步

- 了解 [连接管理](connection.md) 的详细配置
- 学习 [查询操作](query.md) 的各种用法
- 查看 [使用示例](examples.md) 获取更多示例代码

