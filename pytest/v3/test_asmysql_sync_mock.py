import unittest
from unittest.mock import Mock

from pydantic import BaseModel

from asmysql.v3 import AsMysql
from asmysql.v3 import SyncEngine as Engine
from asmysql.v3 import SyncResult as Result


class User(BaseModel):
    id: int
    name: str
    email: str


class Product(BaseModel):
    id: int
    name: str
    price: float


class TestSyncAsMysqlWithMock(unittest.TestCase):
    """使用mock测试AsMysql类的同步版本，避免需要实际数据库连接"""

    def setUp(self):
        """测试前准备"""
        # 创建mock的engine
        self.mock_engine = Mock(spec=Engine)
        self.mock_engine.url = "mysql://localhost:3306/test_db"
        self.mock_engine.host = "localhost"
        self.mock_engine.port = 3306

        # 创建AsMysql实例
        self.asmysql = AsMysql(self.mock_engine)

    def test_asmysql_creation(self):
        """测试AsMysql实例创建"""
        self.assertIsInstance(self.asmysql, AsMysql)
        self.assertEqual(self.asmysql.client, self.mock_engine)
        self.assertEqual(str(self.asmysql), "AsMysql=mysql://localhost:3306/test_db")
        self.assertIn("AsMysql", repr(self.asmysql))

    def test_asmysql_client_property(self):
        """测试AsMysql的client属性"""
        client = self.asmysql.client
        self.assertEqual(client, self.mock_engine)
        self.assertTrue(hasattr(client, "execute"))
        self.assertTrue(hasattr(client, "execute_many"))
        self.assertTrue(hasattr(client, "is_connected"))

    def test_asmysql_execute_query(self):
        """测试AsMysql执行查询语句"""
        # 创建mock的result对象
        mock_result = Mock(spec=Result)
        mock_result.error = None
        mock_result.row_count = 1

        # 配置engine的execute方法返回mock_result
        self.mock_engine.execute = Mock(return_value=mock_result)

        # 测试execute调用
        query = "SELECT * FROM test_users WHERE name = %s"
        result = self.asmysql.client.execute(query, ("张三",))

        # 验证调用
        self.mock_engine.execute.assert_called_once_with(query, ("张三",))
        self.assertEqual(result, mock_result)

    def test_asmysql_execute_many(self):
        """测试AsMysql批量执行语句"""
        # 创建mock的result对象
        mock_result = Mock(spec=Result)
        mock_result.error = None
        mock_result.row_count = 3

        # 配置engine的execute_many方法返回mock_result
        self.mock_engine.execute_many = Mock(return_value=mock_result)

        # 测试execute_many调用
        query = "INSERT INTO test_products (name, price) VALUES (%s, %s)"
        products_data = [("产品1", 100.00), ("产品2", 200.00), ("产品3", 300.00)]
        result = self.asmysql.client.execute_many(query, products_data)

        # 验证调用
        self.mock_engine.execute_many.assert_called_once_with(query, products_data)
        self.assertEqual(result, mock_result)

    def test_asmysql_execute_with_different_result_types(self):
        """测试AsMysql执行查询语句的不同结果类型"""
        # 创建mock的result对象
        mock_result = Mock(spec=Result)
        mock_result.error = None
        mock_result.row_count = 1

        # 配置engine的execute方法返回mock_result
        self.mock_engine.execute = Mock(return_value=mock_result)

        # 测试execute调用使用dict结果类型
        query = "SELECT * FROM test_users WHERE name = %s"
        result = self.asmysql.client.execute(query, ("张三",), result_class=dict)

        # 验证调用
        self.mock_engine.execute.assert_called_with(query, ("张三",), result_class=dict)
        self.assertEqual(result, mock_result)

        # 测试execute调用使用自定义模型结果类型
        result = self.asmysql.client.execute(query, ("张三",), result_class=User)

        # 验证调用
        self.mock_engine.execute.assert_called_with(query, ("张三",), result_class=User)
        self.assertEqual(result, mock_result)

    def test_asmysql_execute_streaming(self):
        """测试AsMysql流式执行查询"""
        # 创建mock的result对象
        mock_result = Mock(spec=Result)
        mock_result.error = None
        mock_result.row_count = None  # 流式查询返回None

        # 配置engine的execute方法返回mock_result
        self.mock_engine.execute = Mock(return_value=mock_result)

        # 测试execute调用使用流式查询
        query = "SELECT * FROM test_users"
        result = self.asmysql.client.execute(query, stream=True)

        # 验证调用
        self.mock_engine.execute.assert_called_with(query, stream=True)
        self.assertEqual(result, mock_result)

    def test_asmysql_execute_for_iteration(self):
        """测试AsMysql执行查询语句的for迭代"""
        # 创建mock的result对象
        mock_result = Mock(spec=Result)
        mock_result.error = None
        
        # 设置迭代器行为
        mock_result.__iter__ = Mock(return_value=mock_result)
        mock_result.__next__ = Mock(
            side_effect=[("张三", "zhangsan@example.com"), ("李四", "lisi@example.com"), StopIteration]
        )

        # 配置engine的execute方法返回mock_result
        self.mock_engine.execute = Mock(return_value=mock_result)

        # 测试for迭代
        query = "SELECT name, email FROM test_users"
        result = self.asmysql.client.execute(query)

        # 验证调用
        self.mock_engine.execute.assert_called_once_with(query)
        self.assertEqual(result, mock_result)

        # 测试for迭代过程
        users = []
        for user in result:
            users.append(user)

        self.assertEqual(len(users), 2)
        self.assertEqual(users[0], ("张三", "zhangsan@example.com"))
        self.assertEqual(users[1], ("李四", "lisi@example.com"))

    def test_asmysql_execute_iterate_method(self):
        """测试AsMysql执行查询语句的iterate方法"""
        # 创建mock的result对象
        mock_result = Mock(spec=Result)
        mock_result.error = None

        # 模拟iterate方法
        def mock_iterate():
            for item in [("张三", "zhangsan@example.com"), ("李四", "lisi@example.com")]:
                yield item

        mock_result.iterate = Mock(return_value=mock_iterate())

        # 配置engine的execute方法返回mock_result
        self.mock_engine.execute = Mock(return_value=mock_result)

        # 测试execute调用
        query = "SELECT name, email FROM test_users"
        result = self.asmysql.client.execute(query)

        # 验证调用
        self.mock_engine.execute.assert_called_once_with(query)
        self.assertEqual(result, mock_result)

        # 测试iterate方法
        users = []
        for user in result.iterate():
            users.append(user)

        self.assertEqual(len(users), 2)
        self.assertEqual(users[0], ("张三", "zhangsan@example.com"))
        self.assertEqual(users[1], ("李四", "lisi@example.com"))

    def test_asmysql_execute_with_context_manager(self):
        """测试AsMysql执行查询语句的with语句"""
        # 创建mock的result对象
        mock_result = Mock(spec=Result)
        mock_result.error = None
        mock_result.__enter__ = Mock(return_value=mock_result)
        mock_result.__exit__ = Mock(return_value=None)

        # 配置engine的execute方法返回mock_result
        self.mock_engine.execute = Mock(return_value=mock_result)

        # 测试with调用
        query = "SELECT * FROM test_users WHERE name = %s"
        result = self.asmysql.client.execute(query, ("张三",))

        # 验证调用
        self.mock_engine.execute.assert_called_once_with(query, ("张三",))
        self.assertEqual(result, mock_result)

    def test_asmysql_direct_for_on_execute_mock(self):
        """测试使用mock直接在 execute 返回结果上使用 for 迭代"""
        # 创建mock的result对象，模拟迭代器行为
        mock_result = Mock(spec=Result)
        mock_result.error = None

        # 设置迭代器
        mock_result.__iter__ = Mock(return_value=mock_result)
        mock_result.__next__ = Mock(
            side_effect=[("张三", "zhangsan@example.com"), ("李四", "lisi@example.com"), StopIteration]
        )

        # 配置engine的execute方法返回mock_result
        self.mock_engine.execute = Mock(return_value=mock_result)

        # 测试直接在 execute 返回结果上使用 for 迭代
        query = "SELECT name, email FROM test_users"
        result = self.asmysql.client.execute(query, result_class=User)

        # 验证调用
        self.mock_engine.execute.assert_called_once_with(query, result_class=User)
        self.assertEqual(result, mock_result)

        # 测试for迭代过程
        users = []
        for user in result:
            users.append(user)

        self.assertEqual(len(users), 2)
        self.assertEqual(users[0], ("张三", "zhangsan@example.com"))
        self.assertEqual(users[1], ("李四", "lisi@example.com"))


if __name__ == "__main__":
    unittest.main()