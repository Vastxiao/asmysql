"""
主要测试类型提示的使用。
"""
import asyncio
from asmysql.v2 import AsMysql, Engine
from pydantic import BaseModel


engine = Engine(url="mysql://root:xiao@192.168.62.195:3306/")


class Mydata(BaseModel):
    user: str
    host: str


class User(BaseModel):
    id: int
    name: str
    email: str


class Test(AsMysql):

    async def test(self):
        print("=== 测试 await 用法 ===")
        result = await self.client.execute("SELECT user, host FROM mysql.user LIMIT 5", result_class=Mydata)
        print(result)

        print("\n=== 测试 async for row in result ===")
        async for row in result:
            print(f" Type: {type(row)} Row: {row}")

        print("\n=== 测试 data = await result.fetch_one() ===")
        # 重新执行查询以获取新的结果对象
        result = await self.client.execute("SELECT user, host FROM mysql.user LIMIT 5", result_class=Mydata)
        data = await result.fetch_one()
        print(data)
        print(f"Type: {type(data)}")

        print("\n=== 测试 data = await result.fetch_many() ===")
        # 重新执行查询以获取新的结果对象
        result = await self.client.execute("SELECT user, host FROM mysql.user LIMIT 5", result_class=Mydata)
        data = await result.fetch_many(3)
        print(data)
        print(f"Type: {type(data)}")

        print("\n=== 测试 data = await result.fetch_all() ===")
        # 重新执行查询以获取新的结果对象
        result = await self.client.execute("SELECT user, host FROM mysql.user LIMIT 5", result_class=Mydata)
        data = await result.fetch_all()
        print(data)
        print(f"Type: {type(data)}")

        print("\n=== 测试 async for item in result.iterate() ===")
        result = await self.client.execute("SELECT user, host FROM mysql.user LIMIT 5", result_class=Mydata)
        async for item in result.iterate():
            print(f"type({type(item)}) {item!r} {item}")

        print("\n=== 测试 async with self.client.execute(...) as result2 ===")
        async with self.client.execute("SELECT user, host FROM mysql.user LIMIT 5", result_class=Mydata) as result2:
            async for item in result2.iterate():
                print(f"type({type(item)}) {item!r} {item}")

        print("\n=== 测试 async for item in self.client.execute(...) ===")
        # 直接在 execute 返回结果上使用 async for 迭代
        async for item in self.client.execute("SELECT user, host FROM mysql.user LIMIT 5", result_class=Mydata):
            print(f"type({type(item)}) {item!r} {item}")

        print("\n=== 测试创建表和复杂查询 ===")
        # 创建测试表
        await self.client.execute("""
        CREATE TABLE IF NOT EXISTS test_users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL
        )
        """)

        # 插入测试数据
        await self.client.execute(
            "INSERT INTO test_users (name, email) VALUES (%s, %s)",
            ("张三", "zhangsan@example.com")
        )

        # 查询数据
        result = await self.client.execute(
            "SELECT id, name, email FROM test_users WHERE name = %s",
            ("张三",),
            result_class=User
        )
        
        print("\n=== 测试 async for item in result (User model) ===")
        async for item in result:
            print(f"type({type(item)}) {item!r} {item}")

        result = await self.client.execute(
            "SELECT id, name, email FROM test_users WHERE name = %s",
            ("张三",),
            result_class=User
        )
        
        print("\n=== 测试 fetch_one (User model) ===")
        user = await result.fetch_one()
        print(f"type({type(user)}) {user!r} {user}")

        print("\n=== 测试直接在 execute 返回结果上使用 async for 迭代 (User model) ===")
        async for user in self.client.execute(
            "SELECT id, name, email FROM test_users WHERE name = %s",
            ("张三",),
            result_class=User
        ):
            print(f"type({type(user)}) {user!r} {user}")

        # 清理测试数据
        await self.client.execute("DROP TABLE IF EXISTS test_users")


async def main():
    await engine.connect()
    await Test(engine).test()
    await engine.disconnect()


if __name__ == "__main__":
    asyncio.run(main())