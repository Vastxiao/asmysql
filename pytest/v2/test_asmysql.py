import unittest
from unittest import IsolatedAsyncioTestCase
from asmysql.v2 import Engine, AsMysql


class TestAsMysql(IsolatedAsyncioTestCase):
    """测试AsMysql类"""

    async def asyncSetUp(self):
        """测试前准备"""
        # 使用测试数据库连接
        self.engine = Engine("mysql://root:password@localhost:3306/test_db")
        await self.engine.connect()
        self.asmysql = AsMysql(self.engine)

    async def asyncTearDown(self):
        """测试后清理"""
        await self.engine.disconnect()

    async def test_asmysql_creation(self):
        """测试AsMysql实例创建"""
        self.assertIsInstance(self.asmysql, AsMysql)
        self.assertEqual(self.asmysql.client, self.engine)
        self.assertEqual(str(self.asmysql), f'AsMysql={self.engine.url}')
        self.assertIn('AsMysql', repr(self.asmysql))

    async def test_asmysql_client_property(self):
        """测试AsMysql的client属性"""
        client = self.asmysql.client
        self.assertEqual(client, self.engine)
        self.assertTrue(hasattr(client, 'execute'))
        self.assertTrue(hasattr(client, 'execute_many'))
        self.assertTrue(hasattr(client, 'is_connected'))

    async def test_asmysql_execute_query(self):
        """测试AsMysql执行查询语句"""
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

        # 查询数据
        select_query = "SELECT * FROM test_users WHERE name = %s"
        result = await self.asmysql.client.execute(select_query, ("张三",), result_dict=True)
        data = await result.fetch_one()
        self.assertIsNotNone(data)
        self.assertEqual(data["name"], "张三")
        self.assertEqual(data["email"], "zhangsan@example.com")

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
        products_data = [
            ("产品1", 100.00),
            ("产品2", 200.00),
            ("产品3", 300.00)
        ]
        result = await self.asmysql.client.execute_many(insert_query, products_data)
        self.assertIsNone(result.error)
        self.assertEqual(result.row_count, 3)

        # 查询所有数据
        select_query = "SELECT * FROM test_products ORDER BY id"
        result = await self.asmysql.client.execute(select_query, result_dict=True)
        data = await result.fetch_all()
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["name"], "产品1")
        self.assertEqual(data[1]["price"], 200.00)
        self.assertEqual(data[2]["name"], "产品3")

        # 清理测试数据
        drop_table = "DROP TABLE IF EXISTS test_products"
        result = await self.asmysql.client.execute(drop_table)
        self.assertIsNone(result.error)


if __name__ == '__main__':
    unittest.main()