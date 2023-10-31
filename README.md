# asmysql

## Introduction

asmysql is a library for using the MySQL asynchronous client, which is a wrapper for aiomysql.

## Features

* Code supports type annotations.
* Very easy to use, simply inherit the AsMysql class for logical development.
* Supports automatic management of the MySQL connection pool and reconnection mechanism.
* Automatically captures and handles MysqlError errors globally.
* Separates statement execution from data retrieval.

## Install

```sh
# Python3.11+
pip install asmysql
```

## Documentation

### Quick Start

```python
import asyncio
from asmysql import AsMysql


class TestAsMysql(AsMysql):
    host = '127.0.0.1'
    port = 3306
    user = 'root'
    password = 'pass'

    async def get_users(self):
        result = await self.client.execute('select user,authentication_string,host from mysql.user')
        if result.err:
            print(result.err)
        else:
            async for item in result.iterate():
                print(item)

                
async def main():
    mysql = await TestAsMysql()
    await mysql.get_users()
    await mysql.disconnect()


asyncio.run(main())
```

### More Usage

```python
import asyncio
from asmysql import AsMysql

class TestAsMysql(AsMysql):
    async def get_users(self):
        result = await self.client.execute('select user,authentication_string,host from mysql.user')
        if result.err:
            print(result.err)
        else:
            return await result.fetch_all()

mysql = TestAsMysql(host='192.168.1.192', port=3306)

async def main():
    await mysql.connect()  # or: await mysql
    print(await mysql.get_users())
    await mysql.disconnect()

asyncio.run(main())
```
