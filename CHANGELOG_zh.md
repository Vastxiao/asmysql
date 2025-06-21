# Change Log

## [1.3.0] - 2025.06.21

### Breaking Changes

* 修改Result的rowcount属性为row_count
* 修改Result的lastrowid属性为last_rowid
* 修改Result的rownumber属性为row_number

## [1.2.0] - 2025.06.20

### Features

* Result暴露cursor属性
* Result新增rowcount、lastrowid、rownumber属性

## [1.1.3] - 2025.05.27

### Features

```python
import asyncio
from asmysql import AsMysql

async def main():
    async with AsMysql() as mysql:
        # execute方法支持commit参数，用于控制是否提交事务，默认自动判断。
        await mysql.client.execute('insert into test(name) values("test")', commit=False)

asyncio.run(main())
```

## [1.1.0] - 2025.02.12

### Features

```python
import asyncio
from asmysql import AsMysql

mysql = AsMysql()

async def main():
    # AsMysql新增方法: async def __call__()
    await mysql()

    print(await mysql.client.execute('select user,host from mysql.user'))

    # 断开mysql连接：
    await mysql.disconnect()

asyncio.run(main())
```

## [1.0.0] - 2024.10.19

### Features

1. 更新Python版本支持范围，最低支持3.9。
2. 更新文档内容。

## [0.2.0] - 2024.10.14

### Features

1. 修复aiomysql对echo参数的处理。
2. 对AsMysql类新增echo_sql_log参数，用于控制aiomysql是否输出执行的sql语句(默认False)。

```python
from asmysql import AsMysql

class TestAsMysql(AsMysql):
    # 这样就可以控制aiomysql库是否在Logging.logger输出执行的sql语句。
    echo_sql_log = True


# 当然，echo_sql_log参数也可以在实例化AsMysql时传入。
async def main():
    async with TestAsMysql(echo_sql_log=True) as mysql:
        result = await mysql.client.execute('select user,authentication_string,host from mysql.user')
        if result.err:
            print(result.err)
        else:
            async for item in result.iterate():
                print(item)
```

## [0.1.4] - 2024.08.15

### Features

#### 1.AsMysql支持异步上下文管理器。

```python
import asyncio
from asmysql import AsMysql

class TestAsMysql(AsMysql):
    async def get_users(self):
        result = await self.client.execute('select user,authentication_string,host from mysql.user')
        if result.err:
            print(result.err)
        else:
            async for item in result.iterate():
                print(item)

async def main():
    async with TestAsMysql() as mysql:
        await mysql.get_users()

if __name__ == '__main__':
    asyncio.run(main())
```

#### 2.在connection中的异常抛出时，使用ConnectionError替代。

## [0.1.1] - 2023.07.25

### Features

> 新增 Result.err_msg 返回exception错误的详情字符串。

## [0.1.0] - 2023.07.16

### Breaking Changes

### Features

> 1. asmysql是对aiomysql封装的简易使用库。
> 2. 支持自动管理mysql连接池，和重连机制。
> 3. 全局自动捕获处理MysqlError错误。
> 4. 分离执行语句和数据获取。
> 5. 直接集成AsMysql类进行逻辑开发。

### Internal

> 初始化项目，开发环境使用poetry进行管理。
