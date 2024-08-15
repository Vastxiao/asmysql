import asyncio
from typing import Optional
from asmysql import AsMysql
from sqlmodel import SQLModel, Field, select


class TblSmsRecord(SQLModel, table=True):
    __tablename__ = "tbl_sms_record"
    id: Optional[int] = Field(default=None, primary_key=True)
    # id: Annotated[int, Field(primary_key=True)] = None
    rid: str
    mobile: str
    pid: Optional[str] = None


class TestAsMysql(AsMysql):
    host = '192.168.62.195'
    port = 3306
    user = 'root'
    password = 'xiao'
    database = 'db_sms'

    async def get_users(self):
        # result = await self.client.execute('select user,authentication_string,host from mysql.user')
        query = select(TblSmsRecord)
        result = await self.client.execute(query.__str__())
        if result.err:
            print(result.err)
        else:
            async for item in result.iterate():
                print(item)


async def main():
    mysql = await TestAsMysql()
    await mysql.get_users()


asyncio.run(main())
