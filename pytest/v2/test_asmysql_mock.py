import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock
from asmysql import Engine, AsMysql, Result


class TestAsMysqlWithMock(IsolatedAsyncioTestCase):
    """使用mock测试AsMysql类，避免需要实际数据库连接"""

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
        self.assertEqual(str(self.asmysql), 'AsMysql=mysql://localhost:3306/test_db')
        self.assertIn('AsMysql', repr(self.asmysql))

    def test_asmysql_client_property(self):
        """测试AsMysql的client属性"""
        client = self.asmysql.client
        self.assertEqual(client, self.mock_engine)
        self.assertTrue(hasattr(client, 'execute'))
        self.assertTrue(hasattr(client, 'execute_many'))
        self.assertTrue(hasattr(client, 'is_connected'))

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
        products_data = [
            ("产品1", 100.00),
            ("产品2", 200.00),
            ("产品3", 300.00)
        ]
        result = self.asmysql.client.execute_many(query, products_data)
        
        # 验证调用
        self.mock_engine.execute_many.assert_called_once_with(query, products_data)
        self.assertEqual(result, mock_result)


if __name__ == '__main__':
    unittest.main()