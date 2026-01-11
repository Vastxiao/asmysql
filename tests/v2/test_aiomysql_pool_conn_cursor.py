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


# noinspection SpellCheckingInspection
async def execute_query_one(pool, query):
    # conn = await pool.acquire()
    # cur = await conn.cursor(aiomysql.SSDictCursor)
    # exec_rows = await cur.execute(query)
    # result = await cur.fetchone()
    # print(f"execute_query_one exec_rows={exec_rows} "
    #       f"result={result} "
    #       f"row_count={cur.rowcount} last_rowid={cur.lastrowid} "
    #       f"row_number={cur.rownumber}")
    # await cur.close()
    # pool.release(conn)

    # conn = await pool.acquire()
    # cur = await conn.cursor(aiomysql.SSDictCursor)
    # try:
    #     cur = await conn.cursor(aiomysql.SSDictCursor)
    #     try:
    #         exec_rows = await cur.execute(query)
    #         result = await cur.fetchone()
    #         print(f"execute_query_one exec_rows={exec_rows} "
    #               f"result={result} "
    #               f"row_count={cur.rowcount} last_rowid={cur.lastrowid} "
    #               f"row_number={cur.rownumber}")
    #         return result
    #     except Exception:
    #         # 如果在执行游标操作时发生异常，确保关闭游标
    #         await cur.close()
    #         raise
    #     finally:
    #         # 正常情况下关闭游标
    #         await cur.close()
    # except Exception:
    #     # 如果在获取游标或执行过程中发生异常，确保释放连接
    #     pool.release(conn)
    # finally:
    #     # 正常情况下释放连接
    #     pool.release(conn)

    conn = await pool.acquire()
    cur = await conn.cursor(aiomysql.SSDictCursor)
    exec_rows = await cur.execute(query)

    # while True:
    #     # result = await cur.fetchone()
    #     # if result is None:
    #     #     print(f"execute_query_one result={result} ")
    #     #     break
    #     # print(f"execute_query_one exec_rows={exec_rows} "
    #     #       f"result={result} "
    #     #       f"row_count={cur.rowcount} last_rowid={cur.lastrowid} "
    #     #       f"row_number={cur.rownumber}")
    #
    #     result = await cur.fetchmany(5)
    #     if not result:
    #         print(f"execute_query_one result={result} ")
    #         break
    #     print(f"execute_query_one exec_rows={exec_rows} "
    #           f"result={result} "
    #           f"row_count={cur.rowcount} last_rowid={cur.lastrowid} "
    #           f"row_number={cur.rownumber}")

    # result = await cur.fetchall()
    result = await cur.fetchone()
    print(
        f"execute_query_one exec_rows={exec_rows} "
        f"result={result} "
        f"row_count={cur.rowcount} last_rowid={cur.lastrowid} "
        f"row_number={cur.rownumber}"
    )

    await cur.close()
    pool.release(conn)


async def main():
    pool = await create_pool()
    # num_queries = 100000
    # num_queries = 1
    # await run_concurrent_queries(pool, num_queries)

    # await execute_query_one(pool, "select * from tbl_sms_record where rid='1111' limit 50")
    await execute_query_one(pool, "select * from tbl_sms_record limit 50")

    pool.close()
    await pool.wait_closed()


asyncio.run(main())
