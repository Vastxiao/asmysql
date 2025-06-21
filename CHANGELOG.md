# Change Log

## [1.3.0] - 2025.06.21

### Breaking Changes

* Changed Result.rowcount attribute to row_count
* Changed Result.lastrowid attribute to last_rowid
* Changed Result.rownumber attribute to row_number

## [1.2.0] - 2025.06.20

### Features

* Expose `cursor` attribute in `Result`.
* Add new attributes `rowcount`, `lastrowid`, and `rownumber` to `Result`.

## [1.1.3] - 2025.05.27

### Features

```python
import asyncio
from asmysql import AsMysql

async def main():
    async with AsMysql() as mysql:
        # execute method supports the commit parameter to control transaction submission, 
        # automatically determined by default.
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
    # AsMysql add function: async def __call__()
    await mysql()

    print(await mysql.client.execute('select user,host from mysql.user'))

    # 断开mysql连接：
    await mysql.disconnect()

asyncio.run(main())
```

## [1.0.0] - 2024.10.19

### Features

1. Update the supported Python version range, with a minimum support of 3.9.
2. Update the documentation content.

## [0.2.0] - 2024.10.14

### Features

1. Fixed the handling of the `echo` parameter in `aiomysql`.
2. Added the `echo_sql_log` parameter to the `AsMysql` class, used to control whether `aiomysql` outputs the executed SQL statements (default is False).

```python
from asmysql import AsMysql

class TestAsMysql(AsMysql):
    # This allows controlling whether the executed SQL statements in aiomysql
    # are output to Logging.logger.
    echo_sql_log = True


# Of course, the `echo_sql_log` parameter can also be passed when instantiating AsMysql.
async def main():
    async with TestAsMysql(echo_sql_log=True) as mysql:
        result = await mysql.client.execute('select user, authentication_string, host from mysql.user')
        if result.err:
            print(result.err)
        else:
            async for item in result.iterate():
                print(item)
```

## [0.1.4] - 2024.08.15

### Features

#### 1. `AsMysql` supports asynchronous context manager.

```python
import asyncio
from asmysql import AsMysql

class TestAsMysql(AsMysql):
    async def get_users(self):
        result = await self.client.execute('select user, authentication_string, host from mysql.user')
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

#### 2. Replaced exceptions in `connection` with `ConnectionError`.

## [0.1.1] - 2023.07.25

### Features

> Added `Result.err_msg` to return a detailed string of the exception error.

## [0.1.0] - 2023.07.16

### Breaking Changes

### Features

> 1. `asmysql` is a simplified wrapper library around `aiomysql`.
> 2. Supports automatic management of MySQL connection pools and reconnection mechanism.
> 3. Automatically captures and handles `MysqlError` globally.
> 4. Separates statement execution and data retrieval.
> 5. Directly integrates the `AsMysql` class for logical development.

### Internal

> Initialized the project, with the development environment managed using `poetry`.
