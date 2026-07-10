from unittest import IsolatedAsyncioTestCase

from pydantic import BaseModel

from asmysql.v3 import AsMysql, AsyncEngine


class User(BaseModel):
    id: int
    name: str
    email: str


class Product(BaseModel):
    id: int
    name: str
    price: float


class TestAsMysql(IsolatedAsyncioTestCase):
    """测试AsMysql类"""

    async def asyncSetUp(self):
        """测试前准备"""
        # 使用测试数据库连接
        self.engine = AsyncEngine("mysql://root:password@localhost:3306/test_db")
        await self.engine.connect()
        self.asmysql = AsMysql(self.engine)

    async def asyncTearDown(self):
        """测试后清理"""
        await self.engine.disconnect()

    async def test_asmysql_creation(self):
        """测试AsMysql实例创建"""
        self.assertIsInstance(self.asmysql, AsMysql)
        self.assertEqual(self.asmysql.client, self.engine)
        self.assertEqual(str(self.asmysql), f"AsMysql={self.engine.url}")
        self.assertIn("AsMysql", repr(self.asmysql))

    async def test_asmysql_client_property(self):
        """测试AsMysql的client属性"""
        client = self.asmysql.client
        self.assertEqual(client, self.engine)
        self.assertTrue(hasattr(client, "execute"))
        self.assertTrue(hasattr(client, "execute_many"))
        self.assertTrue(hasattr(client, "is_connected"))

    async def test_asmysql_execute_query_with_different_result_types(self):
        """测试AsMysql执行查询语句的不同结果类型"""
        # 创建测试表
        create_table = """
        CREATE TABLE IF NOT EXISTS test_users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL
        )
        """
        result = await self.asmysql.client.execute(create_table)
        self.assertIsNone(result.error)

        # 插入测试数据
        insert_query = "INSERT INTO test_users (name, email) VALUES (%s, %s)"
        result = await self.asmysql.client.execute(insert_query, ("张三", "zhangsan@example.com"))
        self.assertIsNone(result.error)
        self.assertEqual(result.row_count, 1)

        # 测试默认tuple结果类型
        select_query = "SELECT * FROM test_users WHERE name = %s"
        result = await self.asmysql.client.execute(select_query, ("张三",))
        self.assertIsNone(result.error)

        # 测试 async for row in result
        count = 0
        async for row in result:
            count += 1
            self.assertIsInstance(row, tuple)
            self.assertEqual(len(row), 3)  # id, name, email
        self.assertEqual(count, 1)

        # 重新执行查询以测试其他方法
        result = await self.asmysql.client.execute(select_query, ("张三",))

        # 测试 fetch_one
        data = await result.fetch_one()
        self.assertIsNotNone(data)
        self.assertIsInstance(data, tuple)
        self.assertEqual(data[1], "张三")
        self.assertEqual(data[2], "zhangsan@example.com")

        # 再次插入数据以测试更多方法
        result = await self.asmysql.client.execute(insert_query, ("李四", "lisi@example.com"))
        self.assertIsNone(result.error)

        # 重新执行查询以测试 fetch_many
        result = await self.asmysql.client.execute(select_query.replace("= %s", "!= %s"), ("不存在的用户",))
        data = await result.fetch_many(1)
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 1)
        self.assertIsInstance(data[0], tuple)

        # 测试 fetch_all
        result = await self.asmysql.client.execute("SELECT * FROM test_users ORDER BY id")
        data = await result.fetch_all()
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 2)
        self.assertIsInstance(data[0], tuple)
        self.assertIsInstance(data[1], tuple)

        # 测试 dict 结果类型
        result = await self.asmysql.client.execute(select_query, ("张三",), result_class=dict)
        data = await result.fetch_one()
        self.assertIsNotNone(data)
        self.assertIsInstance(data, dict)
        self.assertEqual(data["name"], "张三")
        self.assertEqual(data["email"], "zhangsan@example.com")

        # 测试自定义模型结果类型
        result = await self.asmysql.client.execute(select_query, ("张三",), result_class=User)
        data = await result.fetch_one()
        self.assertIsNotNone(data)
        self.assertIsInstance(data, User)
        self.assertEqual(data.name, "张三")
        self.assertEqual(data.email, "zhangsan@example.com")

        # 测试 async for item in result.iterate()
        result = await self.asmysql.client.execute("SELECT * FROM test_users", result_class=User)
        users = []
        async for item in result.iterate():
            users.append(item)
        self.assertEqual(len(users), 2)
        self.assertIsInstance(users[0], User)
        self.assertIsInstance(users[1], User)

        # 测试 async with self.client.execute(...) as result
        async with self.asmysql.client.execute(select_query, ("张三",), result_class=User) as result:
            user_data = None
            async for item in result.iterate():
                user_data = item
            self.assertIsInstance(user_data, User)
            self.assertEqual(user_data.name, "张三")

        # 清理测试数据
        drop_table = "DROP TABLE IF EXISTS test_users"
        result = await self.asmysql.client.execute(drop_table)
        self.assertIsNone(result.error)

    async def test_asmysql_execute_many(self):
        """测试AsMysql批量执行语句"""
        # 创建测试表
        create_table = """
        CREATE TABLE IF NOT EXISTS test_products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            price DECIMAL(10, 2) NOT NULL
        )
        """
        result = await self.asmysql.client.execute(create_table)
        self.assertIsNone(result.error)

        # 批量插入数据
        insert_query = "INSERT INTO test_products (name, price) VALUES (%s, %s)"
        products_data = [("产品1", 100.00), ("产品2", 200.00), ("产品3", 300.00)]
        result = await self.asmysql.client.execute_many(insert_query, products_data)
        self.assertIsNone(result.error)
        self.assertEqual(result.row_count, 3)

        # 查询所有数据
        select_query = "SELECT * FROM test_products ORDER BY id"
        result = await self.asmysql.client.execute(select_query, result_class=dict)
        data = await result.fetch_all()
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["name"], "产品1")
        self.assertEqual(data[1]["price"], 200.00)
        self.assertEqual(data[2]["name"], "产品3")

        # 测试 execute_many 与自定义模型
        result = await self.asmysql.client.execute(select_query, result_class=Product)
        products = []
        async for product in result.iterate():
            products.append(product)
        self.assertEqual(len(products), 3)
        self.assertIsInstance(products[0], Product)
        self.assertIsInstance(products[1], Product)
        self.assertIsInstance(products[2], Product)

        # 测试 execute_many 与 async with
        async with self.asmysql.client.execute(select_query, result_class=Product) as result:
            product_list = []
            async for item in result.iterate():
                product_list.append(item)
            self.assertEqual(len(product_list), 3)
            self.assertIsInstance(product_list[0], Product)

        # 清理测试数据
        drop_table = "DROP TABLE IF EXISTS test_products"
        result = await self.asmysql.client.execute(drop_table)
        self.assertIsNone(result.error)

    async def test_asmysql_execute_streaming(self):
        """测试AsMysql流式执行查询"""
        # 创建测试表
        create_table = """
        CREATE TABLE IF NOT EXISTS test_stream (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        )
        """
        result = await self.asmysql.client.execute(create_table)
        self.assertIsNone(result.error)

        # 插入测试数据
        insert_query = "INSERT INTO test_stream (name) VALUES (%s)"
        data_to_insert = [("数据" + str(i),) for i in range(10)]
        result = await self.asmysql.client.execute_many(insert_query, data_to_insert)
        self.assertIsNone(result.error)
        self.assertEqual(result.row_count, 10)

        # 测试流式查询
        select_query = "SELECT * FROM test_stream"
        result = await self.asmysql.client.execute(select_query, stream=True)
        self.assertIsNone(result.error)
        self.assertIsNone(result.row_count)  # 流式查询应该返回None

        # 测试流式查询的 async for
        count = 0
        async for row in result:
            count += 1
            self.assertIsInstance(row, tuple)
        self.assertEqual(count, 10)

        # 清理测试数据
        drop_table = "DROP TABLE IF EXISTS test_stream"
        result = await self.asmysql.client.execute(drop_table)
        self.assertIsNone(result.error)

    async def test_asmysql_direct_async_for_on_execute(self):
        """测试直接在 execute 返回结果上使用 async for 迭代"""
        # 创建测试表
        create_table = """
        CREATE TABLE IF NOT EXISTS test_direct_iteration (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL
        )
        """
        await self.asmysql.client.execute(create_table)

        # 插入测试数据
        insert_query = "INSERT INTO test_direct_iteration (name, email) VALUES (%s, %s)"
        test_users = [("张三", "zhangsan@example.com"), ("李四", "lisi@example.com"), ("王五", "wangwu@example.com")]

        for user in test_users:
            await self.asmysql.client.execute(insert_query, user)

        # 测试直接在 execute 返回结果上使用 async for 迭代
        # 这是直接在 engine.execute() 返回的结果上使用 async for，而不是先 await 再迭代
        select_query = "SELECT * FROM test_direct_iteration"

        # 测试使用 tuple 类型
        users = []
        async for user in self.asmysql.client.execute(select_query):
            users.append(user)
            self.assertIsInstance(user, tuple)
        self.assertEqual(len(users), 3)

        # 测试使用 dict 类型
        users_dict = []
        async for user in self.asmysql.client.execute(select_query, result_class=dict):
            users_dict.append(user)
            self.assertIsInstance(user, dict)
        self.assertEqual(len(users_dict), 3)

        # 测试使用自定义模型类型
        users_model = []
        async for user in self.asmysql.client.execute(select_query, result_class=User):
            users_model.append(user)
            self.assertIsInstance(user, User)
        self.assertEqual(len(users_model), 3)

        # 清理测试数据
        await self.asmysql.client.execute("DROP TABLE IF EXISTS test_direct_iteration")
