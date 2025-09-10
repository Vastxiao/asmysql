import asyncio
from asmysql import AsMysql


class TestAsMysql(AsMysql):
    host = '192.168.62.195'
    port = 3306
    user = 'root'
    password = 'xiao'
    db = 'test'

    async def get_users(self):
        result = await self.client.execute('select user,authentication_string,host from mysql.user')
        if result.err:
            print(result.err)
        else:
            async for item in result.iterate():
                print(item)


async def main():
    mysql = await TestAsMysql()
    await mysql.get_users()
    await mysql.disconnect()

asyncio.run(main())
