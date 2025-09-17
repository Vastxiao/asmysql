import asyncio
from asmysql import Engine
from asmysql import AsMysql


class TestAsMysql(AsMysql):
    async def print_users(self):
        result = await self.client.execute('select user,host from mysql.user', result_dict=True, stream=True)
        if result.error:
            print(f"error_no: {result.error_no}, error_msg:{result.error_msg}")
        else:
            # result.iterate()是一个异步迭代器，可以获取执行结果的每一行数据
            # async for item in result.iterate():
            #     print(item)
            r = await result.fetch_one()
            print(r)


async def main():
    engine = Engine("mysql://root:xiao@192.168.62.195:3306/")
    await engine.connect()

    test_mysql = TestAsMysql(engine)

    await test_mysql.print_users()

    await engine.disconnect()


asyncio.run(main())
