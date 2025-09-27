import unittest

from asmysql.v3 import AsMysql
from asmysql.v3 import SyncEngine as Engine

engine = Engine("mysql://root:xiao@192.168.62.195:3306/")


def print_engine_status():
    print(f"engine status: {engine.status}")


class TestAsMysql(AsMysql):
    def exec_result_fetch_one(self):
        # 不使用流式查询来测试基础功能
        with self.client.execute("select user,host from mysql.user limit 1") as result:
            print_engine_status()
            if result.error:
                print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
            else:
                data = result.fetch_one()
                print("ooooooooooooooooooooooooooooo", data)
                print_engine_status()

    def exec_result_fetch_many(self):
        # 不使用流式查询来测试基础功能
        with self.client.execute("select user,host from mysql.user limit 5") as result:
            print_engine_status()
            if result.error:
                print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
            else:
                print_engine_status()
                data_list = result.fetch_many(3)
                print(data_list)
                print_engine_status()

    def exec_result_fetch_all(self):
        # 不使用流式查询来测试基础功能
        with self.client.execute("select user,host from mysql.user", result_class=dict) as result:
            print_engine_status()
            if result.error:
                print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
            else:
                print_engine_status()
                data_list = result.fetch_all()
                print(f"Total records: {len(data_list)}")
                print_engine_status()

    def exec_result_iter(self):
        # 使用流式查询进行迭代测试
        with self.client.execute("select user,host from mysql.user", stream=True) as result:
            print_engine_status()
            if result.error:
                print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
            else:
                print_engine_status()
                # result.iterate()是一个迭代器，可以获取执行结果的每一行数据
                count = 0
                for item in result.iterate():
                    print(item)
                    count += 1
                    if count >= 3:  # 限制输出数量
                        break
                print_engine_status()

    def for_result(self):
        # 使用流式查询进行迭代测试
        with self.client.execute("select user,host from mysql.user", stream=True, result_class=dict) as result:
            print_engine_status()
            if result.error:
                print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
            else:
                print_engine_status()
                count = 0
                for item in result:
                    print(item)
                    count += 1
                    if count >= 3:  # 限制输出数量
                        break
                print_engine_status()

    def with_exec_result(self):
        with self.client.execute("select user,host from mysql.user", result_class=dict) as result:
            print_engine_status()
            if result.error:
                print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
            else:
                # result.iterate()是一个迭代器，可以获取执行结果的每一行数据
                count = 0
                for item in result.iterate():
                    print(item)
                    count += 1
                    if count >= 3:  # 限制输出数量
                        break
                print_engine_status()

    def for_item_in_exec(self):
        # 使用流式查询进行迭代测试
        with self.client.execute("select user,host from mysql.user", stream=True, result_class=dict) as result:
            count = 0
            for item in result:
                item: dict
                print(item)
                count += 1
                if count >= 3:  # 限制输出数量
                    break
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
        # test_mysql.exec_result_fetch_many()
        # test_mysql.exec_result_fetch_all()
        # test_mysql.exec_result_iter()
        # test_mysql.for_result()
        # test_mysql.with_exec_result()
        # test_mysql.for_item_in_exec()

        engine.disconnect()
        print_engine_status()


if __name__ == "__main__":
    unittest.main()