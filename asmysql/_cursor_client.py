
import typing
from aiomysql import Pool
from pymysql.err import MySQLError

from ._result import Result


class CursorClient:
    """这个是封装aiomysql的cursor客户端

    这个是 asmysql 内部使用的类，并不会暴露给客户端
    """
    def __init__(self, pool: Pool):
        """执行语句参考：
        https://pymysql.readthedocs.io/en/latest/modules/cursors.html
        """
        self.__pool: Pool = pool

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.__pool.echo} ' \
               f'pool({self.__pool.minsize}, {self.__pool.maxsize})>'

    async def execute(self, query: str,
                      values: typing.Union[typing.Sequence, dict] = None,
                      ) -> Result:
        try:
            async with self.__pool.acquire() as conn:
                async with conn.cursor() as cur:
                    rows = await cur.execute(query, values)
                    await conn.commit()
                    return Result(query, rows=rows, cursor=cur)
        except MySQLError as err:
            return Result(query, err=err)

    async def execute_many(self, query: str,
                           values: typing.Sequence[typing.Union[typing.Sequence, dict]]
                           ) -> Result:
        try:
            async with self.__pool.acquire() as conn:
                async with conn.cursor() as cur:
                    rows = await cur.executemany(query, values)
                    return Result(query, rows=rows, cursor=cur)
        except MySQLError as err:
            return Result(query, err=err)
