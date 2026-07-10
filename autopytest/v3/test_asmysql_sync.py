"""
主要测试v3同步版本AsMysql的使用。
"""

import unittest

from pydantic import BaseModel

from asmysql.v3 import AsMysql, SyncEngine


class Mydata(BaseModel):
    user: str
    host: str


class User(BaseModel):
    id: int
    name: str
    email: str


class TestSyncAsMysql(unittest.TestCase):
    """测试AsMysql类的同步版本，需要实际数据库连接"""

    @classmethod
    def setUpClass(cls):
        """测试类前准备"""
        # 注意：这里需要根据你的实际数据库配置修改连接信息
        cls.engine = SyncEngine(url="mysql://root:password@127.0.0.1:3306/")
        cls.engine.connect()

    @classmethod
    def tearDownClass(cls):
        """测试类后清理"""
        cls.engine.disconnect()

    def test_basic_execute_and_iteration(self):
        """测试基本执行和迭代功能"""
        # 创建AsMysql实例
        asmysql = AsMysql(self.engine)
        
        # 执行查询
        result = asmysql.client.execute("SELECT user, host FROM mysql.user LIMIT 5", result_class=Mydata)
        
        # 验证结果
        self.assertIsNotNone(result)
        
        # 测试迭代
        count = 0
        for row in result:
            self.assertIsInstance(row, Mydata)
            count += 1
            if count >= 5:  # 限制迭代次数
                break

    def test_fetch_operations(self):
        """测试各种fetch操作"""
        asmysql = AsMysql(self.engine)
        
        # 测试 fetch_one
        result = asmysql.client.execute("SELECT user, host FROM mysql.user LIMIT 5", result_class=Mydata)
        data = result.fetch_one()
        self.assertIsInstance(data, Mydata)
        
        # 测试 fetch_many
        result = asmysql.client.execute("SELECT user, host FROM mysql.user LIMIT 5", result_class=Mydata)
        data_list = result.fetch_many(3)
        self.assertIsInstance(data_list, list)
        self.assertLessEqual(len(data_list), 3)
        if data_list:
            self.assertIsInstance(data_list[0], Mydata)
        
        # 测试 fetch_all
        result = asmysql.client.execute("SELECT user, host FROM mysql.user LIMIT 5", result_class=Mydata)
        data_list = result.fetch_all()
        self.assertIsInstance(data_list, list)
        if data_list:
            self.assertIsInstance(data_list[0], Mydata)

    def test_iterate_method(self):
        """测试iterate方法"""
        asmysql = AsMysql(self.engine)
        
        result = asmysql.client.execute("SELECT user, host FROM mysql.user LIMIT 5", result_class=Mydata)
        count = 0
        for item in result.iterate():
            self.assertIsInstance(item, Mydata)
            count += 1
            if count >= 5:
                break

    def test_context_manager(self):
        """测试上下文管理器"""
        asmysql = AsMysql(self.engine)
        
        with asmysql.client.execute("SELECT user, host FROM mysql.user LIMIT 5", result_class=Mydata) as result:
            count = 0
            for item in result.iterate():
                self.assertIsInstance(item, Mydata)
                count += 1
                if count >= 5:
                    break

    def test_database_operations(self):
        """测试完整的数据库操作流程"""
        asmysql = AsMysql(self.engine)
        
        # 创建测试表
        asmysql.client.execute("""
        CREATE TABLE IF NOT EXISTS test_users_pytest (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL
        )
        """)
        
        try:
            # 插入测试数据
            asmysql.client.execute(
                "INSERT INTO test_users_pytest (name, email) VALUES (%s, %s)", 
                ("张三", "zhangsan@example.com")
            )
            
            # 查询数据
            result = asmysql.client.execute(
                "SELECT id, name, email FROM test_users_pytest WHERE name = %s", 
                ("张三",), 
                result_class=User
            )
            
            # 验证结果
            user = result.fetch_one()
            self.assertIsInstance(user, User)
            self.assertEqual(user.name, "张三")
            self.assertEqual(user.email, "zhangsan@example.com")
            
            # 测试直接迭代
            result = asmysql.client.execute(
                "SELECT id, name, email FROM test_users_pytest WHERE name = %s", 
                ("张三",), 
                result_class=User
            )
            
            for user in result:
                self.assertIsInstance(user, User)
                self.assertEqual(user.name, "张三")
                
        finally:
            # 清理测试数据
            asmysql.client.execute("DROP TABLE IF EXISTS test_users_pytest")


if __name__ == "__main__":
    unittest.main()