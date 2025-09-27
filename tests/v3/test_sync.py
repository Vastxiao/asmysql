import unittest

from asmysql.v3 import AsMysql
from asmysql.v3 import SyncEngine as Engine

engine = Engine("mysql://root:xiao@192.168.62.195:3306/")


def print_engine_status():
    print(f"engine status: {engine.status}")


class TestAsMysql(AsMysql):
    def exec_result_fetch_one(self):
        result = self.client.execute("select user,host from mysql.user", stream=True)
        print_engine_status()
        if result.error:
            print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
        else:
            data = result.fetch_one()
            print(data)
            print_engine_status()
            print(result.fetch_one())
            print_engine_status()

    def exec_result_fetch_many(self):
        result = self.client.execute("select user,host from mysql.user", stream=True)
        print_engine_status()
        if result.error:
            print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
        else:
            print_engine_status()
            data_list = result.fetch_many()
            print(data_list)
            print_engine_status()

    def exec_result_fetch_all(self):
        result = self.client.execute("select user,host from mysql.user", stream=True, result_class=dict)
        print_engine_status()
        if result.error:
            print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
        else:
            print_engine_status()
            data_list = result.fetch_all()
            print(data_list)
            print_engine_status()

    def exec_result_iter(self):
        result = self.client.execute("select user,host from mysql.user", stream=True)
        print_engine_status()
        if result.error:
            print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
        else:
            print_engine_status()
            # result.iterate()是一个迭代器，可以获取执行结果的每一行数据
            for item in result.iterate():
                print(item)
            print_engine_status()

    def for_result(self):
        result = self.client.execute("select user,host from mysql.user", stream=True, result_class=dict)
        print_engine_status()
        if result.error:
            print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
        else:
            print_engine_status()
            for item in result:
                print(item)
            print_engine_status()

    def with_exec_result(self):
        with self.client.execute("select user,host from mysql.user", result_class=dict, stream=True) as result:
            print_engine_status()
            if result.error:
                print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
            else:
                # result.iterate()是一个迭代器，可以获取执行结果的每一行数据
                for item in result.iterate():
                    print(item)
                    print_engine_status()
                print_engine_status()

    def for_item_in_exec(self):
        for item in self.client.execute("select user,host from mysql.user", stream=True, result_class=dict):
            item: dict
            print(item)
            print_engine_status()


class TestSync(unittest.TestCase):
    def test_sync_operations(self):
        """测试同步操作"""
        print_engine_status()
        engine.connect()
        print_engine_status()

        test_mysql = TestAsMysql(engine)

        # 测试各种方法
        test_mysql.exec_result_fetch_one()
        test_mysql.exec_result_fetch_many()
        test_mysql.exec_result_fetch_all()
        test_mysql.exec_result_iter()
        test_mysql.for_result()
        test_mysql.with_exec_result()
        test_mysql.for_item_in_exec()

        engine.disconnect()
        print_engine_status()


if __name__ == "__main__":
    unittest.main()