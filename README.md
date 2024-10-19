# asmysql

[![PyPI](https://img.shields.io/pypi/v/asmysql.svg?logo=pypi&logoColor=FFE873)](https://pypi.org/project/asmysql/)
[![Python](https://img.shields.io/pypi/pyversions/asmysql.svg?logo=python&logoColor=FFE873)](https://pypi.org/project/asmysql/)
[![Licence](https://img.shields.io/github/license/Vastxiao/asmysql.svg)](https://github.com/Vastxiao/asmysql/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/badge/asmysql)](https://pepy.tech/project/asmysql)
[![Downloads](https://static.pepy.tech/badge/asmysql/month)](https://pepy.tech/project/asmysql)
[![Downloads](https://static.pepy.tech/badge/asmysql/week)](https://pepy.tech/project/asmysql)

* PyPI: https://pypi.org/project/asmysql/
* GitHub: https://github.com/vastxiao/asmysql
* Gitee: https://gitee.com/vastxiao/asmysql

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
# Install from PyPI
pip install asmysql
```

## Documentation

### Quick Start

```python
import asyncio
from asmysql import AsMysql


# Directly inherit the AsMysql class for development:
class TestAsMysql(AsMysql):
    # You can define some default parameters for the Mysql instance initialization here
    # The attributes are consistent with the __init__ parameters
    host = '127.0.0.1'
    port = 3306
    user = 'root'
    password = 'pass'

    async def get_users(self):
        # The self.client attribute is specifically used to execute SQL statements, providing aiomysql's execute and execute_many methods.
        result = await self.client.execute('select user,authentication_string,host from mysql.user')
        # result is specifically used to obtain execution results, providing fetch_one, fetch_many, fetch_all, and iterate methods.
        # result.err is the exception object (Exception) for all MySQL execution errors.
        if result.err:
            print(result.err_msg)
        else:
            # result.iterate() is an asynchronous iterator that can fetch each row of the execution result.
            async for item in result.iterate():
                print(item)

                
async def main():
    # This will create an instance and connect to MySQL:
    mysql = await TestAsMysql()

    await mysql.get_users()

    # Remember to disconnect the MySQL connection before exiting the program:
    await mysql.disconnect()


asyncio.run(main())
```

### Support for asynchronous context managers.

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
    # Using async with will automatically close the MySQL connection when the code exits.
    async with TestAsMysql() as mysql:
        await mysql.get_users()

if __name__ == '__main__':
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

# When creating a MySQL instance, parameters such as MySQL address and user password can be passed in.
mysql = TestAsMysql(host='192.168.1.192', port=3306)

async def main():
    # This will connect to MySQL:
    await mysql.connect()  # or: await mysql

    print(await mysql.get_users())

    # Disconnect MySQL connection:
    await mysql.disconnect()

asyncio.run(main())
```
