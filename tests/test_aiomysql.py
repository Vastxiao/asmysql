import aiomysql
import asyncio


async def create_pool():
    pool = await aiomysql.create_pool(
        host='192.168.62.195',
        port=3306,
        user='root',
        password='xiao',
        db='db_sms',
        minsize=3,
        maxsize=10
    )
    return pool


async def execute_query(pool, query):
    while True:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query)
                result = await cur.fetchall()
                # return result
                print(result)


async def run_concurrent_queries(pool, num_queries):
    query = "select * from tbl_sms_record"

    async with asyncio.TaskGroup() as tg:
        for tid in range(num_queries):
            # tg.create_task(exec_sql(database.fetch_all, 'show tables', tid))
            tg.create_task(execute_query(pool, query))


async def main():
    pool = await create_pool()
    num_queries = 100000
    await run_concurrent_queries(pool, num_queries)
    pool.close()
    await pool.wait_closed()


asyncio.run(main())
