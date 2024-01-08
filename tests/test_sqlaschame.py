import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# 创建异步引擎
# 替换这里的URL为你的数据库连接字符串
ASYNC_DB_URL = "mysql+aiomysql://user:password@host/dbname"
engine = create_async_engine(ASYNC_DB_URL, echo=True)


# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


# 异步查询示例
async def async_query():
    # 创建一个新的异步会话
    async with AsyncSessionLocal() as session:
        # 异步执行查询
        result = await session.execute(text("SELECT * FROM some_table"))
        # 获取结果
        data = result.fetchall()
        print(data)


# 在异步环境中运行上述查询函数
asyncio.run(async_query())
