"""
主要测试类型提示的使用。
"""
import asyncio
from asmysql import AsMysql, Engine
from pydantic import BaseModel


engine = Engine(url="mysql://root:xiao@192.168.62.195:3306/")


class Mydata(BaseModel):
    user: str
    host: str



class Test(AsMysql):

    async def test(self):
        result = await self.client.execute("SELECT user, host FROM mysql.user LIMIT 5", result_class=Mydata)
        print(result)

        # async for row in result:
        #     print(f" Type: {type(row)} Row: {row}")

        # data = await result.fetch_one()
        # print(data)

        # data = await result.fetch_many()
        # print(data)

        # if result.error:
        #     print(result.error_msg)
        # data = await result.fetch_all()
        # print(data)

        async for item in result.iterate():
            print(f"type({type(item)}) {item!r} {item}")


async def main():
    await engine.connect()
    await Test(engine).test()
    await engine.disconnect()


asyncio.run(main())
