import asyncio
from asmysql import AsMysql


class TestAsMysql(AsMysql):
    host = '192.168.62.195'
    port = 3306
    user = 'root'
    password = 'xiao'
    db = 'db_sms'

    async def get_users(self):
        result = await self.client.execute('select user,host from mysql.user')
        # async for item in result.iterate():
        #     yield item
        if result.err:
            print(result.err)
        else:
            return await result.fetch_many(3)

    async def get_users_with_iterate(self):
        result = await self.client.execute('select user,host from mysql.user')
        async for item in result.iterate():
            yield item


mysql = TestAsMysql()


async def task_run(tg_id: int):
    while True:
        data = await mysql.get_users()
        print(f'task({tg_id}): ', data)


async def task_run_with_iterate(tg_id: int):
    while True:
        async for item in mysql.get_users_with_iterate():
            print(f'task({tg_id}) {item}')


async def main():
    await mysql
    async with asyncio.TaskGroup() as tg:
        for tg_id in range(100000):
            tg.create_task(task_run(tg_id))
            # tg.create_task(task_run_with_iterate(tg_id))


asyncio.run(main())
