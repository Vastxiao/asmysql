import asyncio

import aiomysql


async def create_pool():
    # noinspection PyUnresolvedReferences,SpellCheckingInspection
    pool = await aiomysql.create_pool(
        # host='192.168.62.195', port=3306, user='root', password='xiao',
        host="192.168.63.114",
        port=3306,
        user="4399smsuser",
        password="4399it&trainDB$",
        db="db_sms",
        minsize=3,
        maxsize=10,
        autocommit=True,
        echo=True,
    )
    return pool


async def execute_query_one(pool, query):
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.SSDictCursor) as cur:
            exec_rows = await cur.execute(query)
            # result = await cur.fetchall()
            # print(result)

            num = 0
            while True:
                # row = await cur.fetchmany(5)
                row = await cur.fetchone()
                if not row:
                    break
                num += 1
                print(
                    f"fetchmany num={num} rows={exec_rows} "
                    f"row_count={cur.rowcount} last_rowid={cur.lastrowid} "
                    f"row_number={cur.rownumber} {row}"
                )


async def execute_query(pool, query):
    while True:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.SSCursor) as cur:
                await cur.execute(query)
                result = await cur.fetchall()
                # return result
                print(result)


async def run_concurrent_queries(pool, num_queries):
    query = "select * from tbl_sms_record"

    # noinspection PyUnresolvedReferences
    async with asyncio.TaskGroup() as tg:
        for tid in range(num_queries):
            # tg.create_task(exec_sql(database.fetch_all, 'show tables', tid))
            tg.create_task(execute_query(pool, query))


async def main():
    pool = await create_pool()
    # num_queries = 100000
    # num_queries = 1
    # await run_concurrent_queries(pool, num_queries)

    await execute_query_one(pool, "select * from tbl_sms_record limit 50")

    pool.close()
    await pool.wait_closed()


asyncio.run(main())
