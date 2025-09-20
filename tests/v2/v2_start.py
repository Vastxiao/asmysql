import asyncio
from asmysql import Engine
from asmysql import AsMysql


engine = Engine("mysql://root:xiao@192.168.62.195:3306/")


def print_engine_status():
    print(f"engine status: {engine.status}")


class TestAsMysql(AsMysql):
    async def print_users(self):
        result = await self.client.execute('select user,host from mysql.user', result_dict=True, stream=True)
        print_engine_status()
        if result.error:
            print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
        else:
            # result.iterate()是一个异步迭代器，可以获取执行结果的每一行数据
            # async for item in result.iterate():
            #     print(item)
            r = await result.fetch_one()
            print(r)
            print_engine_status()

    async def print_async_with_users(self):
        # _result = await self.client.execute('select user,host from mysql.user', result_dict=True, stream=True)
        # async with _result as result:
        async with self.client.execute('select user,host from mysql.user', result_dict=True, stream=True) as result:
            print_engine_status()
            if result.error:
                print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
            else:
                # result.iterate()是一个异步迭代器，可以获取执行结果的每一行数据
                async for item in result.iterate():
                    print(item)
                    print_engine_status()
                print_engine_status()

    async def print_async_for_result(self):
        result = await self.client.execute('select user,host from mysql.user', result_dict=True, stream=True)

        async for item in result:
            print_engine_status()
            print(item)
        print_engine_status()

async def main():
    print_engine_status()
    await engine.connect()
    print_engine_status()

    test_mysql = TestAsMysql(engine)

    # await test_mysql.print_users()
    # await test_mysql.print_async_with_users()
    await test_mysql.print_async_for_result()

    await engine.disconnect()
    print_engine_status()

asyncio.run(main())
