"""
测试核心问题：在 autocommit=False 的事务中，执行 USE / SET 是否会触发隐式 commit？
"""
import asyncio
import traceback

import aiomysql

MYSQL_CONFIG = dict(
    host="192.168.62.195",
    port=3306,
    user="root",
    password="xiao",
    autocommit=False,
    db="mysql",
)


async def check_table(cur, label):
    await cur.execute("SELECT DATABASE()")
    db = (await cur.fetchone())[0]
    await cur.execute("SHOW TABLES LIKE 'test_use_commit'")
    exists = (await cur.fetchone()) is not None
    print(f"    [{label}] 当前库={db}, 表存在={exists}", flush=True)
    return exists


async def main():
    pool = await aiomysql.create_pool(
        **MYSQL_CONFIG, connect_timeout=5, minsize=1, maxsize=2,
    )

    conn = await pool.acquire()
    cur = await conn.cursor()

    # ========== 准备：确保干净状态 ==========
    print("[准备] 清理并创建测试表 ...", flush=True)
    await conn.commit()
    await cur.execute("DROP TABLE IF EXISTS test_use_commit")
    await conn.commit()
    await cur.execute("""
        CREATE TABLE test_use_commit (
            id INT PRIMARY KEY AUTO_INCREMENT,
            val VARCHAR(50)
        ) ENGINE=InnoDB
    """)
    await conn.commit()
    await check_table(cur, "创建后")

    try:
        # =====================================================
        # 测试 1: INSERT → USE → ROLLBACK
        # =====================================================
        print("\n--- 测试 1: INSERT → USE → USE 切回 → ROLLBACK ---", flush=True)

        await cur.execute("INSERT INTO test_use_commit (val) VALUES ('before_use')")

        await cur.execute("USE information_schema")
        await cur.execute("USE mysql")
        await check_table(cur, "USE切回后")

        await conn.rollback()
        await check_table(cur, "ROLLBACK后")

        await cur.execute("SELECT COUNT(*) FROM test_use_commit")
        cnt = (await cur.fetchone())[0]
        print(f"    count={cnt} => {'PASS: USE 没有隐式 commit' if cnt == 0 else 'FAIL: USE 触发了隐式 commit'}", flush=True)

        # 测试1结束后做一次干净提交，避免影响测试2
        await conn.commit()
        await check_table(cur, "测试1结束后")

        # =====================================================
        # 测试 2: INSERT → SET → ROLLBACK
        # =====================================================
        print("\n--- 测试 2: INSERT → SET → ROLLBACK ---", flush=True)

        await check_table(cur, "测试2开始前")

        await cur.execute("INSERT INTO test_use_commit (val) VALUES ('before_set')")
        print("    INSERT 完成", flush=True)

        await cur.execute("SET SESSION wait_timeout=200")
        await cur.execute("SET SESSION sql_mode=''")
        await cur.execute("SET NAMES utf8mb4")
        print("    SET 完成", flush=True)

        await check_table(cur, "SET后")

        await conn.rollback()
        await check_table(cur, "ROLLBACK后")

        await cur.execute("SELECT COUNT(*) FROM test_use_commit")
        cnt = (await cur.fetchone())[0]
        print(f"    count={cnt} => {'PASS: SET 没有隐式 commit' if cnt == 0 else 'FAIL: SET 触发了隐式 commit'}", flush=True)

        # 测试2结束后干净提交
        await conn.commit()

        # =====================================================
        # 测试 3 (对照): INSERT → COMMIT
        # =====================================================
        print("\n--- 测试 3 (对照): INSERT → COMMIT ---", flush=True)
        await cur.execute("INSERT INTO test_use_commit (val) VALUES ('committed')")
        await conn.commit()

        await cur.execute("SELECT * FROM test_use_commit")
        rows = await cur.fetchall()
        print(f"    最终数据: {rows}", flush=True)

    except Exception as e:
        print(f"\n!! 异常: {type(e).__name__}: {e}", flush=True)
        traceback.print_exc()
        # 异常时也检查表状态
        try:
            await check_table(cur, "异常时")
        except Exception:
            print("    异常时无法检查表状态", flush=True)

    finally:
        print("\n[清理] ...", flush=True)
        try:
            await conn.commit()
            await cur.execute("DROP TABLE IF EXISTS test_use_commit")
            await conn.commit()
        except Exception as e:
            print(f"    清理异常: {e}", flush=True)
        await cur.close()
        pool.release(conn)
        pool.close()
        await pool.wait_closed()
        print("完成", flush=True)


async def run():
    await asyncio.wait_for(main(), timeout=30)


asyncio.run(run())
