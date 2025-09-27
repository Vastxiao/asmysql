import asyncio

from asmysql.v2 import AsMysql, Engine

engine = Engine("mysql://root:xiao@192.168.62.195:3306/")


def print_engine_status():
    print(f"engine status: {engine.status}")


class TestAsMysql(AsMysql):
    async def await_exec_result_fetch_one(self):
        result = await self.client.execute("select user,host from mysql.user", stream=True)
        print_engine_status()
        if result.error:
            print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
        else:
            data = await result.fetch_one()
            print(data)
            print_engine_status()
            print(await result.fetch_one())

            print_engine_status()

    async def await_exec_result_fetch_many(self):
        result = await self.client.execute("select user,host from mysql.user", stream=True)
        print_engine_status()
        if result.error:
            print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
        else:
            print_engine_status()
            data_list = await result.fetch_many()
            print(data_list)
            print_engine_status()

    async def await_exec_result_fetch_all(self):
        result = await self.client.execute("select user,host from mysql.user", stream=True, result_class=dict)
        print_engine_status()
        if result.error:
            print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
        else:
            print_engine_status()
            data_list = await result.fetch_all()
            print(data_list)
            print_engine_status()

    async def await_exec_result_iter(self):
        result = await self.client.execute("select user,host from mysql.user", stream=True)
        print_engine_status()
        if result.error:
            print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
        else:
            print_engine_status()
            # result.iterate()是一个异步迭代器，可以获取执行结果的每一行数据
            async for item in result.iterate():
                print(item)
            print_engine_status()

    async def await_exec_result_async_for_result(self):
        result = await self.client.execute("select user,host from mysql.user", stream=True, result_class=dict)
        print_engine_status()
        if result.error:
            print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
        else:
            print_engine_status()
            async for item in result:
                print(item)
            print_engine_status()

    async def async_with_exec_result(self):
        async with self.client.execute("select user,host from mysql.user", result_class=dict, stream=True) as result:
            print_engine_status()
            if result.error:
                print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
            else:
                # result.iterate()是一个异步迭代器，可以获取执行结果的每一行数据
                async for item in result.iterate():
                    print(item)
                    print_engine_status()
                print_engine_status()

    async def async_for_item_in_exec(self):
        async for item in self.client.execute("select user,host from mysql.user", stream=True, result_class=dict):
            item: dict
            print(item)
            print_engine_status()


async def main():
    print_engine_status()
    await engine.connect()
    print_engine_status()

    test_mysql = TestAsMysql(engine)

    # await test_mysql.print_users()
    # await test_mysql.async_with_exec_result()
    # await test_mysql.print_async_for_result()
    await test_mysql.async_for_item_in_exec()

    await engine.disconnect()
    print_engine_status()


asyncio.run(main())
