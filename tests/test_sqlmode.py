import asyncio
from typing import Optional
from sqlmodel import SQLModel, Field, select


class TblSmsRecord(SQLModel, table=True):
    __tablename__ = "tbl_sms_record"
    id: Optional[int] = Field(default=None, primary_key=True)
    # id: Annotated[int, Field(primary_key=True)] = None
    rid: str
    mobile: str
    pid: Optional[str] = None


class TestMysql:
    host = '192.168.62.195'
    port = 3306
    user = 'root'
    password = 'xiao'
    database = 'db_sms'

    async def init(self):
        pass
